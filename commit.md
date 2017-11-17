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
