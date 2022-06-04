# About Tykhe

Tykhe is a web app which allows the user to obtain samples from a simulated study (typically psychological or sociological), intended to be used in the teaching of statistical methods. It is named after the ancient Greek goddess of fortune, and the icon is her cornucopia.

Tykhe was created in 2022 by [Carsten Allefeld](https://allefeld.github.io/), with study definitions contributed by [TBD]. The source code is available on [GitHub](https://github.com/allefeld/tykhe).


## Pages

1)  __Preselect parameters__ (`/preselect`) is intended for lecturers. They select a Study and possibly Sample ID, Sample size, and File format, and submit the form, which leads to the second page.

2) __Request sample__ (`/request`) is intended for students, and a URL to this page is typically shared with students by a lecturer. Students may have to select the Sample size or can change it if already filled in. Submitting the form by the button Collect Sample leads to the third page.

3) __Collect sample__ (`/collect`) shows an animation intended to illustrate the process of data collection. After it is finished, a form appears in which the student may have to select the File format or can change it. Submitting the form by the button Download starts a file download.


## Teaching scenarios
    
### In a lab, the lecturer wants to illustrate the effects of random sampling.

On first page, the lecturer selects a Study and possibly other parameters, but leaves the field Sample ID empty. They submit the form and share with students the resulting URL of the second page.

When a student uses that URL, the sample ID is filled in randomly, so that every student gets a different sample.

### In a lab, the lecturer wants to illustrate the effects of sample size.

The lecturer shares with students the URLs resulting from filling in different values for Sample Size; or they leave the field Sample Size empty and instruct students to fill in different values themselves.

### In a test, the lecturer wants every student to work with different data, to discourage one copying the results from another.

They share with students a URL created in the same way as in the first scenario, so that every student gets a different sample. Students are instructed to note their Sample ID (displayed on the third page) in their work.

### Advanced: In marking a test, the lecturer wants to programmatically (e.g. in Python, R, or Matlab code) produce the results that each student should have arrived at.

The lecturer uses the URL they shared with students and proceeds through the second and third page to the file download. They note the URL which delivers the data file, which will be of this form:

````
/download?study=simon&size=20&format=csv&sid=832793
````

In their analysis script, they use modified versions of this URL, where the number `832793` at the end is replaced by each student-specific Sample ID which the student noted in their work. This URL can be used e.g. in Python with `pandas.read_csv`, in R with `read.csv` or in Matlab with `webread`.