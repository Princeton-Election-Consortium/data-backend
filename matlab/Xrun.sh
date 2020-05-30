#!/bin/bash

# Run a command inside a virtual framebuffer

XVFB_DISPLAY=99
Xvfb :$XVFB_DISPLAY -screen 0 1280x1024x24 &
XVFB_PID=$!
export DISPLAY=:$XVFB_DISPLAY
eval "$1"
kill $XVFB_PID
