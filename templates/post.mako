<%inherit file="base.mako"/>
<%namespace name="c" file="components.mako"/>
<article>
  <header class="post-header">
    <h1>${variant.title}</h1>
    <div class="meta">
      % if entry.date:
      <time datetime="${entry.date.isoformat()}">${entry.date.isoformat()}</time> ·
      % endif
      ${variant.reading_minutes} min read
    </div>
    % if entry.has_translation:
    <div class="lang-switch" role="group" aria-label="Language">
      % for lang in entry.langs:
      % if lang == variant.lang:
      <span class="active" aria-current="true">${lang.upper()}</span>
      % else:
      <a href="${entry.url(lang)}" hreflang="${lang}" lang="${lang}"
         title="${lang_names[lang]}">${lang.upper()}</a>
      % endif
      % endfor
    </div>
    % endif
  </header>
  <div class="prose">
    ${variant.html | n}
  </div>
  <footer>
    % if variant.ai_note:
    <p class="ai-note">${variant.ai_note}</p>
    % endif
    ${c.tag_list(entry)}
  </footer>
</article>
