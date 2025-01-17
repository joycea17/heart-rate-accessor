document.getElementById("heartbeat-btn").addEventListener("click", () => {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        navigator.mediaDevices
            .getUserMedia({ video: true })
            .then((stream) => {
                const video = document.getElementById("video-stream");
                video.srcObject = stream;
                video.play();

                const canvas = document.createElement("canvas");
                const context = canvas.getContext("2d");

                const sendFrame = () => {
                    if (!stream.active) return;

                    context.drawImage(video, 0, 0, canvas.width, canvas.height);

                    canvas.toBlob((blob) => {
                        const formData = new FormData();
                        formData.append("video_frame", blob);

                        fetch("/heartbeat", {
                            method: "POST",
                            body: formData,
                        })
                        .then((response) => response.json())
                        .then((data) => {
                            console.log(data);
                            if (data.bpm !== "Calculating...") {
                                document.getElementById("bpm-display").textContent = `Your Heartbeat: ${data.bpm} BPM`;
                            }
                        })
                        .catch((err) => console.error("Error:", err));
                    });

                    setTimeout(sendFrame, 1000 / 30); // 30 FPS
                };

                sendFrame();

                setTimeout(() => {
                    stream.getTracks().forEach((track) => track.stop());
                }, 10000);
            })
            .catch((err) => {
                console.error("Error accessing the camera: ", err);
                alert("Unable to access the camera. Please check permissions.");
            });
    } else {
        alert("Camera not supported in this browser.");
    }
});
