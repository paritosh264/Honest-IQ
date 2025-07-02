   const alth = document.getElementById('alth');
const altbx = document.getElementById('altbx');

  const agree = document.getElementById('agree');
  const startBtn = document.getElementById('startBtn');
  const video = document.getElementById('video');

  agree.addEventListener('change', () => {
    startBtn.style.display = agree.checked ? 'block' : 'none';
  });

  startBtn.addEventListener('click', () => {
    document.getElementById('instructions').style.display = 'none';
    document.getElementById('test').style.display = 'block';
  });

  navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
    video.srcObject = stream;
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    setInterval(() => {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);
      const dataUrl = canvas.toDataURL('image/jpeg');
      fetch('/send_frame', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ frame: dataUrl })
      });
    }, 100);
  });
  setInterval(()=>{
    fetch('/get_alerts').then(
        resp=>resp.json()
    ).then(data=>{
        const alerted=data.alerts;
        if(alerted && alerted.length>0){
            altbx.style.border="5px solid red"
            alth.innerHTML=alerted.join("<br>")

        }else{
            altbx.style.border="5px solid green"
            alth.innerHTML=""

        }
    })
  },100);
