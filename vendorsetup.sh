# Shebang is intentionally missing - do not run as a script

HZ_DIR="vendor/nothing/Pong/proprietary/vendor/lib64"
if [ -f "$HZ_DIR/libhyperzoom.arcsoft.so.part00" ] && \
   [ -f "$HZ_DIR/libhyperzoom.arcsoft.so.part01" ]; then
    cat "$HZ_DIR/libhyperzoom.arcsoft.so.part00" \
        "$HZ_DIR/libhyperzoom.arcsoft.so.part01" \
        > "$HZ_DIR/libhyperzoom.arcsoft.so"
fi
