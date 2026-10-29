<%inherit file="base.mako"/>
<h1>Tags</h1>
% if not tags:
<p class="muted">No tags yet.</p>
% endif
<p class="tags">
% for tag, entries in tags:
  <a class="tag" href="/tags/${tag_slug(tag)}/">#${tag} (${len(entries)})</a>
% endfor
</p>
