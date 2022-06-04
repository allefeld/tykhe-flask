// new random Sample ID for preselect.html

let arandom = document.getElementById('random');
arandom.style.display = '';

let isid = document.getElementById('sid');
let isidMin = parseInt(isid.min);
let isidMax = parseInt(isid.max);

function randomSID() {
  isid.value = Math.floor(Math.random() * (isidMax - isidMin + 1)) + isidMin;
}
