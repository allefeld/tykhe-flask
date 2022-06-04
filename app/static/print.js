// print link for study description in request.html and collect.html

function printStudy(study) {
  url = '/study?study=' + study;
  window.open(url, 'studywindow', 'popup');
  return false;
}

let istudy = document.getElementById('study');
let dstudy = document.getElementsByClassName('study')[0];
let aprint = document.createElement('a');
aprint.className = 'print';
aprint.textContent = '[print]';
aprint.href='javascript:printStudy("' + istudy.value + '")'
dstudy.prepend(aprint);