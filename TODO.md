# TODO

-   available memory and disk don't work
    https://stackoverflow.com/questions/12902253/rails-3-heroku-find-out-dynos-memory-usage
    https://help.heroku.com/TWBM7DL0/how-do-i-measure-current-memory-use-and-max-available-memory-on-a-dyno-in-a-private-space


## future

-   move "data creation and caching" into another module?

-   save study description as pdf

-   missing data

-   trial-level data (hierarchical model)


## obsolete

-   check / improve performance on Heroku
    Can I scale up to more than one dyno on free? – no
    How many apps can I have on free? – 5 unverified, 100 verified
    maybe move to AWS Lambda?

-   Is it possible to move Heroku-specific config (Procfile, runtime) to
    subdirectory – no

-   clean up cache
    maybe not necessary on Heroku, because Dynos are cycled at least once a day

