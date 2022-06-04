// collection animation for collect.html

let dcollect = document.getElementById('collect');
let ddownload = document.getElementById('download');
dcollect.style.display = '';
ddownload.style.display = 'none';

let isize = document.getElementById('size');
let size = isize.value;

// function to create SVG with dots for observations

let w = Math.ceil(Math.sqrt(2 * size));
w = Math.max(w, 20);
let h  = Math.ceil(size / w);

function drawDots(n) {
  let svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
  svg.setAttribute('viewBox', `0 0 ${w} ${h}`);
  dcollect.replaceChildren(svg);

  let y = 0.5;
  let j = n;
  for (let j = n; j > 0; j -= w) {
    let line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    let len = Math.min(j, w);
    let offset = (w - len) / 2;
    line.setAttribute('x1', 0.5 + offset);
    line.setAttribute('x2', len + offset);
    line.setAttribute('y1', y);
    line.setAttribute('y2', y);
    line.setAttribute('stroke-linecap', 'round');
    line.setAttribute('stroke-width', '0.7');
    line.setAttribute('stroke-dasharray', '0,1');
    svg.appendChild(line);
    y = y + 1;
  }
}

// animate dots

// 3 s for 10, 10s for 10,000
let duration = Math.log(size) * 1013 + 667;
let startTime;

function animateDots(timestamp) {
  if (startTime === undefined) {
    startTime = timestamp;
  }
  let time = timestamp - startTime;
  n = Math.min(Math.floor(Math.exp(time / 1000)), size);
  drawDots(n, size);
  if (time < duration) {
    requestAnimationFrame(animateDots);
  } else {
    ddownload.style.display = '';
    ddownload.scrollIntoView();
  }
}

requestAnimationFrame(animateDots);
