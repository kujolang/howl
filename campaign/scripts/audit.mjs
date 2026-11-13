#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {styleSocialSvg} from './social-layout.mjs';
import {fileURLToPath} from 'node:url';
import {createRequire} from 'node:module';
const C=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const releases=path.resolve(process.argv[2]||'');
if(!process.argv[2])throw Error('Usage: node scripts/audit.mjs RELEASES_DIRECTORY');
const require=createRequire(path.join(releases,'lens-source/bridge/package.json'));
const {chromium}=require('playwright-core');
const hash=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const rows=JSON.parse(fs.readFileSync(path.join(C,'catalog.json')));
const receipts=JSON.parse(fs.readFileSync(path.join(C,'evidence/verified/results.json')));
assert.equal(rows.length,12);assert.equal(new Set(rows.map(r=>r.id)).size,12);
for(const name of ['howl','built-with-kujo','verified-with-kujo']){
 const m=JSON.parse(fs.readFileSync(path.join(C,name+'.json')));
 assert.equal(m.cards.length,name==='howl'?12:6);
 assert(m.cards.every(c=>c.variant==='social'));
}
for(const input of JSON.parse(fs.readFileSync(path.join(C,'evidence/input-manifest.json'))))assert.equal(hash(path.join(C,input.path)),input.sha256);
const browser=await chromium.launch();
const page=await browser.newPage({viewport:{width:1200,height:630},deviceScaleFactor:1});
const failures=[];page.on('pageerror',e=>failures.push(e.message));
for(const card of rows){
 const receipt=receipts.find(r=>r.id===card.id);
 assert.equal(receipt.status,'executed-successfully');assert.equal(receipt.exit_code,0);
 assert.equal(hash(path.join(C,card.file)),receipt.source_sha256);
 for(const artifact of receipt.artifacts)assert.equal(hash(path.join(C,'evidence/verified',card.id,artifact.path)),artifact.sha256);
 assert.equal(fs.readFileSync(path.join(C,'gallery',card.id+'.svg'),'utf8'),styleSocialSvg(fs.readFileSync(path.join(C,'generated/howl',card.id+'.svg'),'utf8')));
 for(const ext of ['md'])assert.equal(hash(path.join(C,'gallery',card.id+'.'+ext)),hash(path.join(C,'generated/howl',card.id+'.'+ext)));
 for(const ext of ['html','svg','md','png'])assert(fs.statSync(path.join(C,'gallery',card.id+'.'+ext)).size>0);
 const png=fs.readFileSync(path.join(C,'gallery',card.id+'.png'));assert.equal(png.readUInt32BE(16),1200);assert.equal(png.readUInt32BE(20),630);
 const post=fs.readFileSync(path.join(C,'posts',card.id+'.txt'),'utf8').trim();
 assert(post.endsWith(card.upstream));assert(post.replace(/https:\/\/\S+/g,'x'.repeat(23)).length<=280);
 await page.goto('file://'+path.join(C,'gallery',card.id+'.svg'));await page.evaluate(()=>document.fonts.ready);
 const bounds=await page.locator('text').evaluateAll(elements=>elements.map(e=>{const b=e.getBBox();return {text:e.textContent,x:b.x,y:b.y,right:b.x+b.width,bottom:b.y+b.height,cls:e.getAttribute('class')};}));
 assert(bounds.every(b=>b.x>=42&&b.y>=42&&b.right<=1158&&b.bottom<=588),card.id+': SVG text leaves frame');
 assert(bounds.filter(b=>/social-title|social-tag/.test(b.cls)).every(b=>b.bottom<215),card.id+': text overlaps code preview');
 assert.equal(await page.locator('rect[fill="url(#wash)"], rect[filter="url(#grain)"], rect[x="78"][y="570"]').count(),0);
}
let htmlCount=0,linkCount=0;
for(const file of fs.readdirSync(path.join(C,'gallery')).filter(f=>f.endsWith('.html'))){
 const html=fs.readFileSync(path.join(C,'gallery',file),'utf8');htmlCount++;
 for(const [,href] of html.matchAll(/(?:href|src)="([^"]+)"/g)){
  if(/^(https?:|data:|#)/.test(href))continue;
  assert(fs.existsSync(path.resolve(C,'gallery',href.split('#')[0])),file+': broken link '+href);linkCount++;
 }
}
const galleryChecks=[];
for(const [name,width] of [['desktop',1280],['mobile',390]]){
 await page.setViewportSize({width,height:900});await page.goto('file://'+path.join(C,'gallery/index.html'));
 await page.locator('img').evaluateAll(imgs=>imgs.forEach(img=>img.loading='eager'));
 await page.evaluate(async()=>{await document.fonts.ready;await Promise.all([...document.images].map(i=>i.decode()));});
 const state=await page.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,images:document.images.length,font:document.fonts.check('16px Departure'),collections:[...document.querySelectorAll('.collection')].map(e=>e.textContent)}));
 assert.equal(state.overflow,false);assert.equal(state.images,12);assert.equal(state.font,true);assert.equal(state.collections.length,2);
 await page.screenshot({path:path.join(C,'evidence/gallery-'+name+'.png'),fullPage:true});galleryChecks.push({viewport:name,width,...state});
}
// Compact visual QA sheet, produced by the browser from the actual social SVGs.
await page.setViewportSize({width:1200,height:900});
await page.goto('file://'+path.join(C,'gallery/index.html'));
await page.evaluate(()=>{document.body.innerHTML='<main style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;padding:10px">'+[...document.querySelectorAll('.preview')].map(i=>'<img style="width:100%" src="'+i.getAttribute('src')+'">').join('')+'</main>';});
await page.evaluate(()=>Promise.all([...document.images].map(i=>i.decode())));
await page.screenshot({path:path.join(C,'evidence/contact-sheet.png'),fullPage:true});
assert.deepEqual(failures,[]);
const layouts=JSON.parse(fs.readFileSync(path.join(C,'evidence/render.json'))).codeLayouts;
assert.equal(layouts.length,12);assert(layouts.every(l=>l.fontSize>=26&&l.bottom<=558&&l.width===1024&&l.foreground==='#ffffff'&&l.background==='#111111'));
const result={code_font_min_px:26,code_font_max_px:30,code_contrast:'white on #111111; no wash or grain overlay',bottom_left_accent:false,examples:12,executed:12,manifests:3,collection_counts:[6,6],social_svg:12,png:12,png_size:[1200,630],posts:12,post_length_rule:'<=280 with URLs weighted as 23',publication_html:htmlCount,checked_local_links:linkCount,source_and_artifact_hashes:'pass',publication_markdown_identical_to_howl:true,publication_svg_matches_documented_transform:true,svg_text_bounds_and_code_separation:'pass',gallery_checks:galleryChecks,browser_errors:failures};
fs.writeFileSync(path.join(C,'evidence/artifact-audit.json'),JSON.stringify(result,null,2)+'\n');
await browser.close();console.log(JSON.stringify(result));
