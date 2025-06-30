  const video = document.getElementById('video');

    navigator.mediaDevices.getUserMedia({ video: true })
      .then(br=> {
        
        video.srcObject = br;
      })
      .catch(err => {
        console.error("Error accessing webcam:", err);
      });
