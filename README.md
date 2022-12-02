# ![](app/static/tykhe.svg) Tykhe

Tykhe is a web app implemented in Python / Flask which allows the user to obtain samples from a simulated study (typically psychological or sociological), intended to be used in the teaching of statistical methods. It is named after the ancient Greek goddess of fortune, and the icon is her cornucopia.

The user can select from several different studies, specify sample size and file format, virtually 'collect' a sample, and download the data as a file. In addition, it is possible to specify a 'Sample ID' which determines which data are (pseudo-) randomly generated. This ID is usually randomly generated itself, but can also be specified explicitly to reproduce the same data.

For more information, see the [About Tykhe](app/templates/_about.md) page of the app.

## Running locally

Clone the repository into a directory and make sure all dependencies in `requirements.txt` are installed, preferably in a separate environment. Then run from the root directory:

````
gunicorn app:app
````

## Deploy to Heroku or Render

This repository contains all files necessary for deployment to Heroku (`Procfile`, `runtime.txt`, `app.json`) or Render (`.render-buildpacks.json`, `Dockerfile.render`, `render.yaml`).

***

This software is copyrighted © 2022 by Carsten Allefeld and released under the terms of the GNU General Public License, version 3 or later.
<!-- Study definitions were contributed by [TBD]. -->
