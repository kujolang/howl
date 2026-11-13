// Small presentation lexer for the campaign's Kujo, JSON, and Bash excerpts.
// Coloring never rewrites source: token values concatenate to the exact input.
export const palette = {
  plain:'#f1f5f9', keyword:'#c792ea', string:'#a5d6a7', number:'#ffcb6b',
  function:'#82d7ff', property:'#9cdcfe', variable:'#ffd580',
  operator:'#ffab91', comment:'#a7b0be'
};
export const escapeCode = s => s.replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');
const keywords = new Set(['func','return','await','async','while','loop','try','except','if','else','for','in','mut','let','spawn','from','import','export']);
const constants = new Set(['true','false','null']);
export function highlight(code, language) {
  const pattern = /"(?:\\[\s\S]|[^"\\])*"|'(?:\\[\s\S]|[^'\\])*'|#[^\n]*|\/\/[^\n]*|\$\{[^}]*\}|\$[A-Za-z_]\w*|--[a-z][a-z-]*|\b\d+(?:\.\d+)?\b|[A-Za-z_]\w*|:=|==|!=|<=|>=|&&|\|\||[+*=<>!]|\s+|[\s\S]/g;
  const tokens=[];
  for(const match of code.matchAll(pattern)) {
    const value=match[0], next=code.slice(match.index+value.length).trimStart();
    let kind='plain';
    if(value.startsWith('"')||value.startsWith("'")) kind=language==='json'&&next.startsWith(':')?'property':'string';
    else if(value.startsWith('#')||(language!=='bash'&&value.startsWith('//')))kind='comment';
    else if(value.startsWith('$'))kind='variable';
    else if(/^\d/.test(value)||constants.has(value))kind='number';
    else if(language==='kujo'&&keywords.has(value))kind='keyword';
    else if(/^[A-Za-z_]\w*$/.test(value)&&next.startsWith('('))kind='function';
    else if(language==='bash'&&value.startsWith('--'))kind='property';
    else if(/^(?::=|==|!=|<=|>=|&&|\|\||[+*=<>!])$/.test(value))kind='operator';
    tokens.push({kind,value});
  }
  if(tokens.map(t=>t.value).join('')!==code)throw Error('Syntax highlighting changed source');
  const html=tokens.map(({kind,value})=>kind==='plain'?escapeCode(value):`<span style="color:${palette[kind]};white-space:pre">${language==='bash'&&kind==='string'&&value.startsWith('"')?escapeCode(value).replace(/\$[A-Za-z_]\w*/g,v=>`<span style="color:${palette.variable}">${v}</span>`):escapeCode(value)}</span>`).join('');
  return {html,kinds:[...new Set(tokens.map(t=>t.kind))]};
}
