<%def name="entry_list(entries)">
% if not entries:
<p class="muted">Nothing here yet.</p>
% else:
<ul class="entries">
% for entry in entries:
  <li class="entry">
    <a class="entry-title" href="${entry.url()}">${entry.main.title}</a>
    <div class="meta">
      % if entry.date:
      <time datetime="${entry.date.isoformat()}">${entry.date.isoformat()}</time> ·
      % endif
      ${entry.main.reading_minutes} min read
      % if entry.section:
      · ${entry.section}
      % endif
      % if entry.has_translation:
      % for lang in entry.langs:
      <span class="badge">${lang.upper()}</span>
      % endfor
      % endif
    </div>
    % if entry.main.summary:
    <p class="summary">${entry.main.summary}</p>
    % endif
  </li>
% endfor
</ul>
% endif
</%def>

<%def name="tag_list(entry)">
% if entry.tags:
<p class="tags">
% for tag in entry.tags:
  <a class="tag" href="/tags/${tag_slug(tag)}/">#${tag}</a>
% endfor
</p>
% endif
</%def>
