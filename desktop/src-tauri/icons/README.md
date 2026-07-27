# Application icons

Tauri needs a set of platform icons here before it can build installers. They
are generated artifacts, so they are **not** committed — only the source image
`../../app-icon.png` (1024×1024) is.

Generate the full set locally with:

```bash
# from the desktop/ folder
npm install
npm run tauri icon app-icon.png
```

That command populates this folder with every size/format the bundler expects
(`32x32.png`, `128x128.png`, `128x128@2x.png`, `icon.icns`, `icon.ico`, plus the
Windows Store logos). The CI release workflow runs the same command
automatically. The paths are already referenced in `../tauri.conf.json` under
`bundle.icon`.

To use your own artwork, replace `../../app-icon.png` with a square PNG and
re-run the command.
