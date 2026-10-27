path = r'D:/artweb/src/app/admin/(dashboard)/homepage/page.tsx'
with open(path, 'r', encoding='utf-8') as f:
    s = f.read()

old = '''export default async function HomepagePage() {
  const { supabase } = await requireAdmin();

  // `*` keeps this page working even before the image-column migration has
  // been applied (missing fields simply stay undefined).
  const { data: homepageData, error } = await supabase
    .from("homepage_sections")
    .select("*");'''

new = '''export default async function HomepagePage() {
  const { supabase } = await requireAdmin();

  // `*` keeps this page working even before the image-column migration has
  // been applied (missing fields simply stay undefined).
  const [{ data: homepageData, error }, { data: featuredArtworks, error: artworksError }] =
    await Promise.all([
      supabase.from("homepage_sections").select("*"),
      supabase.from("artworks").select("*").eq("featured", true),
    ]);'''

if old not in s:
    raise SystemExit('nf')
s2 = s.replace(old, new)
old2 = '''  };\n\n  const { data: featuredArtworks, error: artworksError } = await supabase\n    .from("artworks")\n    .select("*")\n    .eq("featured", true);'''
if old2 in s2:
    s2 = s2.replace(old2, '  };')
with open(path, 'w', encoding='utf-8') as f:
    f.write(s2)
print('ok')
