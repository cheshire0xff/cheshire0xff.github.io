<%inherit file="base.mako"/>
<%namespace name="c" file="components.mako"/>
<section class="intro">
  <h1>${site.title}</h1>
  <p>${site.description}</p>
</section>
<h2>Latest</h2>
${c.entry_list(entries)}
