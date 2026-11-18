import type { APIRoute } from 'astro';
const pages=['','agents/','qualification/','local-edition/','community/','demo/','architecture/','showcase/','docs/'];
export const GET: APIRoute = () => {
  const base='https://tec-wel.github.io/HealthQualify/';
  const xml='<?xml version="1.0" encoding="UTF-8"?>' +
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
    pages.map(path=>'<url><loc>'+base+path+'</loc></url>').join('') + '</urlset>';
  return new Response(xml,{headers:{'Content-Type':'application/xml; charset=utf-8'}});
};
