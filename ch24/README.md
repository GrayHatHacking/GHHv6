
# Instructions

## Build
The `Dockerfile` contains the environment needed for the labs.
```
# docker build -t kali .
```

## Use
To run the tests the host's KVM device needs to be redirected to the container.
The `./labs` directory is mounted in `/labs` inside the container.
```
# docker run --device=/dev/kvm -it kali bash
```


