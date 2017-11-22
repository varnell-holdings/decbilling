22-11-2017

- add option to just display anaesthetic report
- change anaesthetic report to upper/lower vs first/second
- fund scraping working
- episode_scrape returns postcode

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
