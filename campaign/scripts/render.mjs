#!/usr/bin/env node
// Campaign assets only. Howl's application and renderers are never edited.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
import {spawnSync} from 'node:child_process';
import {styleSocialSvg} from './social-layout.mjs';
import {highlight, palette} from './syntax-highlight.mjs';
const C=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const releases=path.resolve(process.argv[2] || '');
if(!process.argv[2]) throw Error('Usage: node scripts/render.mjs RELEASES_DIRECTORY');
const require=createRequire(path.join(releases,'lens-source/bridge/package.json'));
const {chromium}=require('playwright-core');
const catalog=JSON.parse(fs.readFileSync(path.join(C,'catalog.json'),'utf8'));
const results=JSON.parse(fs.readFileSync(path.join(C,'evidence/verified/results.json'),'utf8'));
if(results.length!==12 || results.some(r=>r.status!=='executed-successfully')) throw Error('Twelve verified examples required');
const esc=s=>s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const font=fs.readFileSync(path.join(C,'assets/DepartureMono-Regular.woff2')).toString('base64');
const logo=fs.readFileSync(path.join(C,'assets/kujo-logomark-black.svg')).toString('base64');
const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});
const style=`@font-face{font-family:Departure;src:url(data:font/woff2;base64,${font})}*{box-sizing:border-box}body{margin:0;background:white;color:black;font-family:Departure,monospace}.panel{position:absolute;left:64px;top:222px;width:1072px;height:354px;background:#111}pre{position:absolute;left:88px;top:242px;width:1024px;margin:0;white-space:pre-wrap;overflow-wrap:normal;tab-size:4;color:#f1f5f9;font:30px/35px Departure,monospace}.mark{position:absolute;left:1080px;top:58px;width:48px;height:48px}.label{position:absolute;right:64px;top:192px;font-size:12px;letter-spacing:1px}`;
const commands=[];
const codeLayouts=[];
function howl(args){
 const cmd=path.join(releases,'howl-source/bin/howl');
 const p=spawnSync(cmd,args,{cwd:C,env:{...process.env,KUJO:path.join(releases,'kujo')},encoding:'utf8'});
 commands.push({command:[cmd,...args],exit_code:p.status,stdout:p.stdout,stderr:p.stderr});
 if(p.status!==0) throw Error(p.stdout+p.stderr);
}
const all=[];
for(const card of catalog){
 let previewFile=card.file, from=0, to=11;
 if(card.id==='eval'){previewFile='inputs/eval.json';from=4;to=11;}
 if(card.id==='workcell'){previewFile='inputs/workcell.json';from=8;to=12;}
 if(card.id==='lens'){previewFile='inputs/dashboard.json';from=18;to=27;}
 if(card.id==='runledger'){from=8;to=14;}
 if(card.id==='packwrite'){from=2;to=6;}
 if(card.id==='shipcheck'){from=2;to=4;}
 const sourceCode=fs.readFileSync(path.join(C,previewFile),'utf8').split('\n').slice(from,to).join('\n').trimEnd();
 let code=sourceCode;
 // Reflow this long CLI invocation at argument boundaries, preserving every word.
 if(card.id==='shipcheck'){
   code=code.replace(' run ', ' run \\\n  ').replace('gate --dir ', 'gate \\\n  --dir ').replace(' --format ', ' \\\n  --format ');
 }
 const shellWords=s=>s.replace(/\\\r?\n/g,' ').match(/"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|[^\s]+/g);
 const sourcePreserved=code===sourceCode||(card.id==='shipcheck'&&JSON.stringify(shellWords(code))===JSON.stringify(shellWords(sourceCode)));
 if(!sourcePreserved)throw Error('Preview changed source tokens');
 const language=previewFile.endsWith('.json')?'json':previewFile.endsWith('.kujo')?'kujo':'bash';
 const colored=highlight(code,language);
 // Source tokens are preserved; only presentation and verified CLI line continuations change.
 await page.setContent(`<!doctype html><html lang="en"><head><style>${style}</style></head><body><img class="mark" alt="Kujo" src="data:image/svg+xml;base64,${logo}"><div class="label">SOURCE EXCERPT</div><div class="panel"></div><pre>${colored.html}</pre></body></html>`);
 await page.evaluate(()=>document.fonts.ready);
 const layout=await page.locator('pre').evaluate((e,expected)=>{
   if(e.textContent!==expected)throw Error('Highlighted DOM differs from source');
   const maxHeight=310;
   let chosen=null;
   // Preserve source line structure first. Wrap only when no readable size fits.
   for(const wrapping of ['pre','pre-wrap']){
     e.style.whiteSpace=wrapping;
     for(let size=44;size>=26;size-=2){
       const leading=Math.round(size*1.16*10)/10;
       e.style.fontSize=size+'px';e.style.lineHeight=leading+'px';
       if(e.getBoundingClientRect().height<=maxHeight&&e.scrollWidth<=1024){chosen={size,leading,wrapping};break;}
     }
     if(chosen)break;
   }
   if(!chosen)throw Error('Code does not fit at the minimum readable font size');
   const rows=Math.round(e.getBoundingClientRect().height/chosen.leading);
   const leading=Math.min(Math.floor(maxHeight/rows*10)/10,chosen.size*1.65);
   e.style.lineHeight=leading+'px';
   const height=e.getBoundingClientRect().height;
   e.style.top=(222+(354-height)/2)+'px';
   const box=e.getBoundingClientRect();
   return {fontSize:chosen.size,lineHeight:leading,wrapping:chosen.wrapping,visualRows:rows,top:box.top,bottom:box.bottom,height:box.height,width:box.width,foreground:'#f1f5f9',background:'#111111',textMatchesPreview:e.textContent===expected};
 },code);
 if(layout.bottom>558||layout.top<240)throw Error('Code preview overflows: '+card.id);
 codeLayouts.push({id:card.id,language,previewFile,fromLine:from+1,toLine:to,tokenKinds:colored.kinds,sourcePreserved,...layout});
 await page.screenshot({path:path.join(C,'assets',card.id+'-code.png')});
 const raw=fs.readFileSync(path.join(C,'evidence/verified',card.id,'stdout.txt'),'utf8').trimEnd();
 // Large JSON reports remain in evidence; no fabricated shortened output is substituted.
 const output=raw.length<=850 ? raw : '';
 const post=card.post+'\n\n'+card.upstream;
 if(card.post.length+2+23>280)throw Error('X post too long: '+card.id);
 fs.writeFileSync(path.join(C,'posts',card.id+'.txt'),post+'\n');
 all.push({id:card.id,title:card.title,tagline:card.tagline,file:card.file,language:card.repo==='kujo'?'kujo':'bash',variant:'social',label:card.collection,url:card.upstream,show_url:false,font_file:'assets/DepartureMono-Regular.woff2',background_image:'assets/'+card.id+'-code.png',alt:card.collection+': '+card.title+'. '+card.tagline,concepts:[card.collection],expected_output:output,caption:post,cta:'',notes:card.problem+' '+card.notes+' Output shown here, when present, was observed in evidence/verified/'+card.id+'/stdout.txt. Full commands and artifacts are in the verification report.'});
}
for(const [name,cards] of [['built-with-kujo',all.slice(0,6)],['verified-with-kujo',all.slice(6)],['howl',all]]){
 const manifest={project:{name:name==='howl'?'Kujo':cards[0].label,tagline:'Real examples. Recorded execution. Clear limits.',url:'https://kujolang.ai'},cards};
 fs.writeFileSync(path.join(C,name+'.json'),JSON.stringify(manifest,null,2)+'\n');
 howl(['validate','--manifest',name+'.json']);
 howl(['render','--manifest',name+'.json','--out','generated/'+name,'--max-code-lines','60','--max-output-lines','30']);
}
const rawDir=path.join(C,'generated/howl'), gallery=path.join(C,'gallery');fs.mkdirSync(gallery,{recursive:true});
// Publication-only CSS: preserve original Howl outputs under generated/.
const skin=`<style>@font-face{font-family:Departure;src:url(data:font/woff2;base64,${font})}body,pre,code{font-family:Departure,monospace!important}:root{--accent:#111;--code-bg:#111;--code-fg:#eee}*{border-radius:0!important}a,.links a{color:#111!important;text-decoration:underline!important}pre.out{background:#f6f6f6}.wrap{max-width:1200px}.preview{display:block;width:100%;height:auto;margin:0 0 20px}.item{padding:24px}.collection{font-size:24px;margin:32px 0 0}.item .links{line-height:2.2}.campaign-nav{margin:24px 0}.campaign-nav a{margin-right:20px}footer{color:#666}</style>`;
for(const filename of fs.readdirSync(rawDir)){
 const source=path.join(rawDir,filename),target=path.join(gallery,filename);
 if(filename.endsWith('.svg')){fs.writeFileSync(target,styleSocialSvg(fs.readFileSync(source,'utf8')));continue;}
 if(!filename.endsWith('.html')){fs.copyFileSync(source,target);continue;}
 let html=fs.readFileSync(source,'utf8').replace('</head>',skin+'</head>');
 if(filename==='index.html'){
   html=html.replace('</header>','<nav class="campaign-nav"><a href="../VERIFICATION.md">Verification report</a><a href="../POSTS.md">12 X drafts</a><a href="../README.md">Run these examples</a></nav></header>');
   for(let i=0;i<catalog.length;i++){
     const card=catalog[i];const needle='<article class="item">\n<h2>'+esc(card.title)+'</h2>';
     const heading=i===0||i===6?'<h2 class="collection">'+card.collection+'</h2>':'';
     html=html.replace(needle,heading+'<article class="item">\n<a href="'+card.id+'.html"><img loading="lazy" class="preview" src="'+card.id+'.svg" alt="'+esc(card.title+' — '+card.tagline)+'"></a><h2>'+esc(card.title)+'</h2>');
     html=html.replace('<a href="'+card.id+'.md">Markdown</a>','<a href="'+card.id+'.md">Markdown</a><a href="'+card.id+'.png">PNG</a><a href="../evidence/verified/'+card.id+'/receipt.json">Execution receipt</a><a href="../posts/'+card.id+'.txt">X draft</a>');
   }
 } else {
   const id=filename.slice(0,-5);
   html=html.replace('<main class="card">','<main class="card"><nav><a href="index.html">All examples</a> · <a href="../evidence/verified/'+id+'/receipt.json">Execution receipt</a></nav>');
 }
 fs.writeFileSync(target,html);
}
for(const card of catalog){
 await page.goto('file://'+path.join(gallery,card.id+'.svg'));
 await page.evaluate(()=>document.fonts.ready);
 await page.screenshot({path:path.join(gallery,card.id+'.png')});
}
fs.writeFileSync(path.join(C,'evidence/render.json'),JSON.stringify({commands,codeLayouts,syntaxPalette:palette,browser:await browser.version(),conversion:'Playwright Chromium screenshot of publication-styled Howl SVG, 1200x630, deviceScaleFactor 1; awaited document.fonts.ready'},null,2)+'\n');
await browser.close();
fs.writeFileSync(path.join(C,'POSTS.md'),'# X drafts\n\nNot published. Links point to pinned source. Each draft fits 280 characters with X URL weighting (23 characters per URL).\n\n'+catalog.map(c=>'## '+c.collection+' — '+c.title+'\n\n'+c.post+'\n\n'+c.upstream+'\n').join('\n'));
console.log('Rendered 12 social cards, two collection galleries, combined gallery, PNGs and X drafts.');
