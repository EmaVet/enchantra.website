# Building pages for enchantratarot.com

Read this before you change or create any page on this site. The full rulebook, with the reasons behind each rule, is the project doc `claude/WEBSITE_DESIGN_RULES.md` in the Claude project "Enchantra Website". If the two ever differ, the project doc wins and this file gets updated.

## The rules that keep us from going backwards

1. **The homepage is the source of truth.** Every page is built from the homepage's own sections and styles (`index.html`): its `<head>` styles, nav, hero, section patterns, buttons, footer and scripts. Never build a page on a separate or simpler template. That is what made Beta look like a different site.
2. **Widths.** Hero 1180px. Every other section 1080px. Gutters `clamp(18px, 5vw, 40px)`. The nav lines up with the 1180 container. Narrower inner widths only where the homepage has them: pricing 640px (920px from 900px wide), founder section 1080px, FAQ 800px (1080px from 1024px), final call to action 720px.
3. **Alignment.** Left-aligned by default. Centred only for: pricing, "Inside Enchantra", "From one cycle to many", the final call to action, the Almanac front-page hero (approved "wide": 1180px box, headline 960px, intro 700px), and short section intros where the homepage already centres them. Never centre a section to "vary the rhythm". **Centred blocks:** use the full container; headline `max-width` about 960px (hero) or 800px (section) so it is two lines, at most three, on a laptop; intro about 700px; `text-wrap: balance` on the headline and `pretty` on the paragraph. On phones it just wraps inside the gutters and stays centred. Never a narrow cap like 620px (four squashed lines).
4. **Pictures alternate sides.** A picture-and-words section puts the picture on one side and the next one flips it (homepage: Your cards = picture right, A reading to reflect with = picture left, Traditions = decks left, words right). On phones, words come first unless the picture is the point (Dragon Dreaming photo of M).
5. **Headings.** Section H2: `clamp(30px, 2.2vw + 14px, 44px)`, weight 400, serif, `text-wrap: balance`. Hero H1 and the final call to action are larger (see the rulebook). Reading pages (articles, legal) keep smaller in-text subheadings on purpose. Never shrink headings by widening the container.
6. **Nothing floats on wide screens.** No narrow card alone in the middle of a wide page. At 1024px and up, long sections use two columns (heading or picture on one side, content on the other) or a full-width band.
7. **Images.** Code-drawn moons, cards and sparks first. Real photos of M's own decks are welcome. Never redraw, cut out or recreate a real card; show the photograph. Keep approved photo treatments exactly as approved.
8. **Colour is voice.** Gold = the oracle and the one forward action. Sage = the person's own words. Lilac = structure and echoes. Silver = moonlight. Rose = care. No red, no success green. Icons follow the same colours.
9. **Words.** Never change M's copy while doing design work. If copy looks wrong, list it and ask.
10. **Buttons.** Waitlist: "Join the waitlist" (gold, spark first, arrow after). Keepers: "Email to become a Keeper" (mailto with the subject filled in). Never use an email address as button text. One waitlist button on screen at a time on phones.

## How we work

- **Show before changing.** For any design change, render it and send before and after images. For anything open-ended, mock up two or three options and let M choose.
- **Approved means exact.** Put an approved mock-up in exactly as shown. Compare the page with the mock-up (pixel diff) before reporting it done. If you think it needs a change, ask first.
- **Never push without M saying "push".** Pushing to `main` publishes the live site immediately. Commit locally and wait.
- **Check every page at 390, 768, 1024, 1440 and 1920px wide.** No sideways scroll at any width. Check phones as carefully as laptops.
- **Compare against the last approved version**, not only your previous step, so drift is caught (`git diff <approved commit> -- index.html`).
- **Before pushing, fetch.** A GitHub Action commits `sitemap.xml` after every push; if a push is refused, `git fetch` and `git rebase origin/main`, then push again.
- **After pushing, verify live** (fetch the page with a cache-buster). The site is cached for 10 minutes; tell M to hard refresh (Cmd+Shift+R).

## Technical traps

- An ancestor with `transform` (the `.reveal` scroll animation) traps `position: absolute` children. For full-bleed images inside a revealed section, set `transform: none` on the wrappers.
- Inline `style=""` beats stylesheet rules unless the rule uses `!important`. Check inline styles on elements you restyle.
- Don't put test or mock-up pages in this folder; anything here can be published.
