// Publication styling only; keep the released Howl renderer and raw output intact.
export function styleSocialSvg(source) {
  const required=[
    '<rect width="1200" height="630" fill="url(#wash)"/>',
    '<rect width="1200" height="630" filter="url(#grain)" opacity=".7"/>',
    '<rect x="78" y="570" width="84" height="4" fill="#111"/>'
  ];
  let svg=source;
  for(const element of required){
    if(!svg.includes(element))throw Error('Howl social layout changed: '+element);
    svg=svg.replace(element,'');
  }
  svg=svg.replace(/<text x="[^"]+" y="[^"]+" class="mono label">/g,'<text x="64" y="78" class="mono label">');
  svg=svg.replace(/<text x="[^"]+" y="[^"]+" class="mono social-title">/g,'<text x="64" y="150" class="mono social-title">');
  svg=svg.replace(/<text x="[^"]+" y="[^"]+" class="mono social-tag">/g,'<text x="64" y="195" class="mono social-tag">');
  return svg.replace('</svg>', '<style>.social-title{font-size:52px;letter-spacing:-1px}.social-tag{font-size:22px;fill:#111}.label{font-size:16px;letter-spacing:3px}</style>\n</svg>');
}
