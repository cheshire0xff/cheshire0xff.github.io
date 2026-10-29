<!doctype html>
<html lang="${page.lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${page.title if page.path == "/" else page.title + " · " + site.title}</title>
  <meta name="description" content="${page.description or site.description}">
  <link rel="canonical" href="${site.url}${page.path}">
  % for lang, url in page.alternates:
  <link rel="alternate" hreflang="${lang}" href="${site.url}${url}">
  % endfor
  <link rel="alternate" type="application/rss+xml" title="${site.title}" href="/rss.xml">
  <link rel="stylesheet" href="/style.css">
  <script>
    (function () {
      var theme = localStorage.getItem("theme");
      if (theme) { document.documentElement.dataset.theme = theme; }
    })();
  </script>
</head>
<body>
  <header class="site-header">
    <a class="brand" href="/">${site.title}</a>
    <nav>
      % for href, label in nav:
      <a href="${href}">${label}</a>
      % endfor
      <button id="theme-toggle" type="button" aria-label="Toggle dark mode">◐</button>
    </nav>
  </header>
  <main>
    ${next.body()}
  </main>
  <footer class="site-footer">
    <a href="/tags/">Tags</a> · <a href="/rss.xml">RSS</a>
  </footer>
  <script src="/theme.js"></script>
</body>
</html>
