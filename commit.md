
5-1-2017

- calendar added
- landing page for EpisodeFullException
- selective scraping of fund details depending on fund

22-12-2017

- add refering gp scraper
- make seperate episode_close function
- write episodes medical data to csv file
- hard wire weekly target into analysis
- don't scrape insurance if asa is None
- dont do  bill_process if asa is None
- bug fix in redo - inputer upacking too many variables
- added a check that fund membership details panel is present in get_fund


30-11-2017

- added another check to episode_open. A screeshot called aileen.png is checked for
- change order in episode. Now scrape first and check that mrn isdigit
- anaesthetic report now an html file


18-11-2017

- wrote function close_out() to close the open file in Blue Chip
- added logging of crashes and a shortcut to open the log docbill.txt
- separate uninsured and pensioners and add billing message in bill_process not inputbill
- changed ? improved input bill UX - cursor stays on one line

17-11-2017

- bug fixes
- new choice open web site
- now serving today.html locally from D:Nobue
- got rid of offsite() and home.aone.net.au
- fix crash in episode update

5-11-2017

- use dataset to write anaesthetic details to db and get report of today's anaesthetics
- realised can use id to sort database records therefore don't need a date in sortable format -> removed it from to db tuple
- refactor into three files
- Fixed crash in analysis caused by absent csv file  - used try/except
