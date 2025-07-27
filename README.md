# Geochem Streamlit

## Introduction

Hello!

For the past few weeks, I have been working on an App that lets you quickly build
scatter plots, box plots, and TAS-diagram (classification plot) directly from Google
Sheets.

It is convenient for collaborative work: the link to the Google Sheet is always up to
date, everyone can edit the data, and see results shown immediately in the plot.
I have now launched open testing of the GeoQuick app for visualizing geochemical data.

You can try it here: [Geochem App](https://geochem-app-x8wt6zxsp6csnwztd9nvgz.streamlit.app/).

## Features

What you can do:
- Upload your own database and play with sliders (styles, filters);
- Use the demo dataset (from _Marfin et al. (2024)_) to see the app's features;

I would really appreciate it if you could leave your feedback here or via the the
Google Form link in the app.

## Details

More details for those interested.

Why is it needed if Excel exists?

The idea came when my colleagues and I were entering data into a shared database.
Often, someone would update the file, and everyone had to be notified, or it became
unclear which version was correct.

Google Sheets solves some of these issues, but building complex plots with groups using
the standard tools is inconvenient: group settings get reset, and styles are lost,
especially when you have more than five groups, it starts to be extremely annoying.

So, I decided to make GeoQuick: a simple, intuitive tool that works in your browser, 
requires no installation, lets you quickly make basic plots, set up groupings and
styles, and share results.

What’s implemented:
- Data loading (CSV, link to Google Sheet);
- Creating plots (scatter, boxplot, TAS) in a few clicks;
- Grouping data;
- Numerical filters ("AND" logic, the order of filters is not important);
- Choosing a variable to display on hover;
- Save and export graphs to PNG;
- Interactive: zoom and move the plot;

Pros:
- No registration or installation required, works online;
- Does not store your data: everything is deleted when the page is refreshed;

Who might find it useful:
- Geochemists, students, researchers;
- Anyone who analyzes chemical data (not just geological data),
and needs scatter or box plots;

Technical notes (for correct operation):
- Column headers must begin with a letter (e.g., SiO2, Al2O3) or an underscore
(_87Sr_86Sr);
- Headings must not contain spaces, “>”, “<”, quotation marks, or other special
characters;
- Only numbers should be used in data cells (for proper plotting);
- The grouping variable must be text, not numeric (e.g., sample name, group name,
formations, etc.);
- The file must be in CSV or Google Sheets format;

Limitations during testing:
The application runs on a free cloud, so there may be slight delays, especially when
uploading large tables or when several users are using this application at the same time.

After refreshing the page, all data is reset; the application does not save uploaded
tables.

Since this app is currently in the pre-testing phase, I really need feedback: bugs,
suggestions, usability issues, missing features.

Try it here: [Geochem App](https://geochem-app-x8wt6zxsp6csnwztd9nvgz.streamlit.app/)

## Feedback

Please share your suggestions and questions in the comments, via private message, or
through the Google Form in the app.

Thank you for any help!
P.S. If you know anyone who might be interested, please share this post or tag your
friends/colleagues!
