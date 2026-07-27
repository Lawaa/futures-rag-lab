// Prevents an additional console window on Windows in release builds.
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::net::TcpStream;
use std::path::PathBuf;
use std::thread;
use std::time::Duration;

use tauri::menu::{MenuBuilder, MenuItemBuilder, SubmenuBuilder};
use tauri::{Manager, Url};
use tauri_plugin_opener::OpenerExt;
use tauri_plugin_shell::process::CommandEvent;
use tauri_plugin_shell::ShellExt;

const BACKEND_HOST: &str = "127.0.0.1";
const BACKEND_PORT: u16 = 8000;

fn backend_url() -> String {
    format!("http://{BACKEND_HOST}:{BACKEND_PORT}")
}

/// Resolve the user-writable data directory, mirroring the Python backend's
/// layout so the "Open Data Folder" action points at the exact place documents
/// are read from.
fn user_data_dir() -> PathBuf {
    let home = home_dir();
    let base = if cfg!(target_os = "windows") {
        std::env::var("APPDATA")
            .map(PathBuf::from)
            .unwrap_or_else(|_| home.join("AppData").join("Roaming"))
    } else if cfg!(target_os = "macos") {
        home.join("Library").join("Application Support")
    } else {
        std::env::var("XDG_DATA_HOME")
            .map(PathBuf::from)
            .unwrap_or_else(|_| home.join(".local").join("share"))
    };
    base.join("FuturesTradingAssistant").join("data")
}

fn home_dir() -> PathBuf {
    std::env::var("HOME")
        .or_else(|_| std::env::var("USERPROFILE"))
        .map(PathBuf::from)
        .unwrap_or_else(|_| PathBuf::from("."))
}

/// Block until the backend accepts TCP connections (up to ~60 seconds).
fn wait_for_backend() {
    for _ in 0..120 {
        if TcpStream::connect((BACKEND_HOST, BACKEND_PORT)).is_ok() {
            return;
        }
        thread::sleep(Duration::from_millis(500));
    }
}

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            // 1. Launch the bundled Python backend as a sidecar process. The
            //    sidecar is a fully self-contained executable (Python + all
            //    dependencies), so the host machine needs nothing preinstalled.
            let sidecar = app.shell().sidecar("rag-backend")?;
            let (mut rx, _child) = sidecar.spawn()?;
            tauri::async_runtime::spawn(async move {
                while let Some(event) = rx.recv().await {
                    match event {
                        CommandEvent::Stdout(bytes) | CommandEvent::Stderr(bytes) => {
                            eprintln!("[backend] {}", String::from_utf8_lossy(&bytes));
                        }
                        _ => {}
                    }
                }
            });

            // 2. Native menu with "Open Data Folder" so technical users can add
            //    or remove source documents to expand the knowledge base.
            let open_data =
                MenuItemBuilder::with_id("open_data", "Open Data Folder").build(app)?;
            let file_menu = SubmenuBuilder::new(app, "File")
                .item(&open_data)
                .separator()
                .quit()
                .build()?;
            let menu = MenuBuilder::new(app).item(&file_menu).build()?;
            app.set_menu(menu)?;
            app.on_menu_event(move |app, event| {
                if event.id() == open_data.id() {
                    let dir = user_data_dir();
                    let _ = std::fs::create_dir_all(&dir);
                    let _ = app.opener().open_path(dir.to_string_lossy(), None::<&str>);
                }
            });

            // 3. Once the backend answers, point the main window at the web UI.
            let handle = app.handle().clone();
            thread::spawn(move || {
                wait_for_backend();
                if let Some(window) = handle.get_webview_window("main") {
                    if let Ok(url) = Url::parse(&backend_url()) {
                        let _ = window.navigate(url);
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running the Futures Trading Assistant");
}
