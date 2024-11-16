# TODO


## future

-   move "data creation and caching" into another module?

-   save study description as pdf

-   missing data

-   trial-level data (hierarchical model)

-   additional "studies":

    -   rTMS and depression, within-subject and between-subjects, but properly:
        depression scale measures depression, not happiness
        within-subject is more powerful than between-subjects
        placebo and sequence effects
    
    -   sex and gender
        realistic statistics regarding male / female / intersex
        and women / men / other identities
        including possible dependency
        data maybe from studies in https://www.theparadoxinstitute.com/read/a-response-to-stop-using-phony-science-to-justify-transphobia?s=09

-   look at https://github.com/joke2k/faker & https://github.com/ropensci/charlatan


## obsolete

-   check / improve performance on Heroku
    Can I scale up to more than one dyno on free? – no
    How many apps can I have on free? – 5 unverified, 100 verified
    maybe move to AWS Lambda?

-   Is it possible to move Heroku-specific config (Procfile, runtime) to
    subdirectory – no

-   clean up cache
    maybe not necessary on Heroku, because Dynos are cycled at least once a day

