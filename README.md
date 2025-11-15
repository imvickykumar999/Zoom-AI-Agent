# `Zoom Meeting` : [`Deployed`](https://zoomeet.pythonanywhere.com/)

<img width="1535" height="1023" alt="image" src="https://github.com/user-attachments/assets/e2f74cc5-d337-4668-88ba-203b1073baa3" />

```bash
# export your keys from https://marketplace.zoom.us/user/build
export ZOOM_CLIENT_ID="your_actual_zoom_client_id"
export ZOOM_CLIENT_SECRET="your_actual_zoom_client_secret"

# it will generate zoom_token.json
python main.py

# pull zoom-flask-app image
docker pull ghcr.io/imvickykumar999/zoom-flask-app:latest

# run at port 5000
docker run -p 5000:5000 \
  -e ZOOM_CLIENT_ID=your_client_id \
  -e ZOOM_CLIENT_SECRET=your_client_secret \
  -v $(pwd)/zoom_token.json:/app/zoom_token.json \
  ghcr.io/imvickykumar999/zoom-flask-app:latest
```

![image](https://github.com/user-attachments/assets/9c366026-c16a-42eb-afd2-a11f2df84987)
![image](https://github.com/user-attachments/assets/aea542dd-8fe4-4116-9f42-b8652519bb4d)
![image](https://github.com/user-attachments/assets/acd1d7e0-36fa-4e9f-b6b7-933eadfc4b6d)
