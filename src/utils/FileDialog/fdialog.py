import contextlib
import os
import time
from glob import glob

import dearpygui.dearpygui as dpg
import psutil

from src.utils import AlignmentType, auto_align

last_click_time = 0


class FileDialog:
    """
    Arguments:
        title:                  Sets the file dialog window name
        tag:                    Sets the file dialog tag
        width:                  Sets the file dialog window width
        height:                 Sets the file dialog window height
        min_size:               Sets the file dialog minimum size
        dirs_only:              When true it will only list directories
        default_path:           The default path when File dialog starts, if it's cwd it will be the cwd
        file_filter:            If it's for example .py it will only list that type of files
        callback:               When the Ok button has pressed it will call the defined function
        show_dir_size:          When true it will list the directories with the size of the directory
        allow_drag:             When true it will allow to the user to drag the file or folder to a group
        multi_selection:         If true it will allow the user to select multiple files and folder
        show_shortcuts_menu:    A child window containing different shortcuts and of the esternal and internal drives
        no_resize:              When true the window will not be able to resize
        modal:                  A sort of popup effect (can cause problems when the file dialog is activated by a modal)
        saving:                 When true it will allow the user to save files instead of opening them
    Returns:
        Window
    """

    def __init__(
        self,
        title="File Dialog",
        tag="file_dialog",
        width=950,
        height=650,
        min_size=(460, 320),
        dirs_only=False,
        default_path=".",
        file_filter=".*",
        callback=None,
        show_dir_size=False,
        allow_drag=True,
        multi_selection=True,
        show_shortcuts_menu=True,
        no_resize=True,
        modal=True,
        saving=False,
    ):
        # args
        self.selec_alignt = None
        self.size_alignt = None
        self.title = title
        self.tag = tag
        self.width = width
        self.height = height
        self.min_size = min_size
        self.dirs_only = dirs_only
        self.default_path = default_path
        self.file_filter = file_filter
        self.callback = callback
        self.show_dir_size = show_dir_size
        self.allow_drag = allow_drag
        self.multi_selection = multi_selection
        self.show_shortcuts_menu = show_shortcuts_menu
        self.no_resize = no_resize
        self.modal = modal
        self.saving = saving

        self.PAYLOAD_TYPE = "ws_" + self.tag
        self.selected_files = []
        self.selec_height = 16

    def init(self):
        # file dialog theme

        with dpg.theme() as selec_alignt:
            self.selec_alignt = selec_alignt
            with dpg.theme_component(dpg.mvThemeCat_Core):
                dpg.add_theme_style(dpg.mvStyleVar_SelectableTextAlign, x=0, y=0.5)

        with dpg.theme() as size_alignt:
            self.size_alignt = size_alignt
            with dpg.theme_component(dpg.mvThemeCat_Core):
                dpg.add_theme_style(dpg.mvStyleVar_SelectableTextAlign, x=1, y=0.5)

        # texture loading
        def load_image(image_name):
            image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images", image_name)
            return dpg.load_image(image_path)

        diwidth, diheight, dichannels, didata = load_image("document.png")
        afiwidth, afiheight, afichannels, afidata = load_image("add_folder.png")
        afwidth, afheight, afchannels, afdata = load_image("add_file.png")
        mfwidth, mfheight, mfchannels, mfdata = load_image("mini_folder.png")
        fiwidth, fiheight, fichannels, fidata = load_image("folder.png")
        mdwidth, mdheight, mdchannels, mddata = load_image("mini_document.png")
        mewidth, meheight, mechannels, medata = load_image("mini_error.png")
        rwidth, rheight, rchannels, rdata = load_image("refresh.png")
        hdwidth, hdheight, hdchannels, hddata = load_image("hd.png")
        pwidth, pheight, pchannels, pdata = load_image("picture.png")
        bpwidth, bpheight, bpchannels, bpdata = load_image("big_picture.png")
        pfwidth, pfheight, pfchannels, pfdata = load_image("picture_folder.png")
        dwidth, dheight, dchannels, ddata = load_image("desktop.png")
        vwidth, vheight, vchannels, vdata = load_image("videos.png")
        mwidth, mheight, mchannels, mdata = load_image("music.png")
        dfwidth, dfheight, dfchannels, dfdata = load_image("downloads.png")
        dcfwidth, dcfheight, dcfchannels, dcfdata = load_image("documents.png")
        swidth, sheight, schannels, sdata = load_image("search.png")

        # low-level
        self.ico_document = [diwidth, diheight, didata]
        self.ico_add_folder = [afiwidth, afiheight, afidata]
        self.ico_add_file = [afwidth, afheight, afdata]
        self.ico_mini_folder = [mfwidth, mfheight, mfdata]
        self.ico_folder = [fiwidth, fiheight, fidata]
        self.ico_mini_document = [mdwidth, mdheight, mddata]
        self.ico_mini_error = [mewidth, meheight, medata]
        self.ico_refresh = [rwidth, rheight, rdata]
        self.ico_hard_disk = [hdwidth, hdheight, hddata]
        self.ico_picture = [pwidth, pheight, pdata]
        self.ico_big_picture = [bpwidth, bpheight, bpdata]
        self.ico_picture_folder = [pfwidth, pfheight, pfdata]
        self.ico_desktop = [dwidth, dheight, ddata]
        self.ico_videos = [vwidth, vheight, vdata]
        self.ico_music_folder = [mwidth, mheight, mdata]
        self.ico_downloads = [dfwidth, dfheight, dfdata]
        self.ico_document_folder = [dcfwidth, dcfheight, dcfdata]
        self.ico_search = [swidth, sheight, sdata]

        # high-level
        with dpg.texture_registry():
            dpg.add_static_texture(
                width=self.ico_document[0],
                height=self.ico_document[1],
                default_value=self.ico_document[2],
                tag="ico_document_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_add_folder[0],
                height=self.ico_add_folder[1],
                default_value=self.ico_add_folder[2],
                tag="ico_add_folder_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_add_file[0],
                height=self.ico_add_file[1],
                default_value=self.ico_add_file[2],
                tag="ico_add_file",
            )
            dpg.add_static_texture(
                width=self.ico_mini_folder[0],
                height=self.ico_mini_folder[1],
                default_value=self.ico_mini_folder[2],
                tag="ico_mini_folder_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_folder[0],
                height=self.ico_folder[1],
                default_value=self.ico_folder[2],
                tag="ico_folder_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_mini_document[0],
                height=self.ico_mini_document[1],
                default_value=self.ico_mini_document[2],
                tag="ico_mini_document_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_mini_error[0],
                height=self.ico_mini_error[1],
                default_value=self.ico_mini_error[2],
                tag="ico_mini_error_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_refresh[0],
                height=self.ico_refresh[1],
                default_value=self.ico_refresh[2],
                tag="ico_refresh_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_hard_disk[0],
                height=self.ico_hard_disk[1],
                default_value=self.ico_hard_disk[2],
                tag="ico_hard_disk_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_picture[0],
                height=self.ico_picture[1],
                default_value=self.ico_picture[2],
                tag="ico_picture_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_big_picture[0],
                height=self.ico_big_picture[1],
                default_value=self.ico_big_picture[2],
                tag="ico_big_picture_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_picture_folder[0],
                height=self.ico_picture_folder[1],
                default_value=self.ico_picture_folder[2],
                tag="ico_picture_folder_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_desktop[0],
                height=self.ico_desktop[1],
                default_value=self.ico_desktop[2],
                tag="ico_desktop_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_videos[0],
                height=self.ico_videos[1],
                default_value=self.ico_videos[2],
                tag="ico_videos_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_music_folder[0],
                height=self.ico_music_folder[1],
                default_value=self.ico_music_folder[2],
                tag="ico_music_folder_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_downloads[0],
                height=self.ico_downloads[1],
                default_value=self.ico_downloads[2],
                tag="ico_downloads_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_document_folder[0],
                height=self.ico_document_folder[1],
                default_value=self.ico_document_folder[2],
                tag="ico_document_folder_" + self.tag,
            )
            dpg.add_static_texture(
                width=self.ico_search[0],
                height=self.ico_search[1],
                default_value=self.ico_search[2],
                tag="ico_search_" + self.tag,
            )

            self.img_document = "ico_document_" + self.tag
            self.img_add_folder = "ico_add_folder_" + self.tag
            self.img_add_file = "ico_add_file_" + self.tag
            self.img_mini_folder = "ico_mini_folder_" + self.tag
            self.img_folder = "ico_folder_" + self.tag
            self.img_mini_document = "ico_mini_document_" + self.tag
            self.img_mini_error = "ico_mini_error_" + self.tag
            self.img_refresh = "ico_refresh_" + self.tag
            self.img_hard_disk = "ico_hard_disk_" + self.tag
            self.img_picture = "ico_picture_" + self.tag
            self.img_big_picture = "ico_big_picture_" + self.tag
            self.img_picture_folder = "ico_picture_folder_" + self.tag
            self.img_desktop = "ico_desktop_" + self.tag
            self.img_videos = "ico_videos_" + self.tag
            self.img_music_folder = "ico_music_folder_" + self.tag
            self.img_downloads = "ico_downloads_" + self.tag
            self.img_document_folder = "ico_document_folder_" + self.tag
            self.img_search = "ico_search_" + self.tag

    def start(self):
        # low-level functions
        def _get_all_drives():
            all_drives = psutil.disk_partitions()
            drive_list = [drive.device for drive in all_drives if drive.device]
            return drive_list

        def delete_table():
            for child in dpg.get_item_children("explorer", 1):
                dpg.delete_item(child)

        def get_file_size(file_path):
            # Get the file size in bytes

            if os.path.isdir(file_path):
                if self.show_dir_size:
                    total = 0
                    for path, _dirs, files in os.walk(file_path):
                        for f in files:
                            fp = os.path.join(path, f)
                            total += os.path.getsize(fp)
                    file_size_bytes = total
                else:
                    file_size_bytes = "-"
            elif os.path.isfile(file_path):
                file_size_bytes = os.path.getsize(file_path)

            # Define the units and their respective sizes
            size_units = [
                ("TB", 2**40),  # Tebibyte
                ("GB", 2**30),  # Gibibyte
                ("MB", 2**20),  # Mebibyte
                ("KB", 2**10),  # Kibibyte
                ("B", 1),  # Byte
            ]

            # Determine the appropriate unit for formatting
            if file_size_bytes != "-":
                for unit, size_limit in size_units:
                    if file_size_bytes >= size_limit:
                        # Calculate the size in the selected unit
                        file_size = file_size_bytes / size_limit
                        # Return the formatted size with the unit
                        return f"{file_size:.0f} {unit}"
            else:
                return "-"

            # If the file size is smaller than 1 byte or unknown
            return "0 B"  # or "Unknown" or any other desired default

        def on_path_enter():
            try:
                chdir(dpg.get_value("ex_path_input"))
            except FileNotFoundError:
                message_box("Invalid path", "No such file or directory")

        def message_box(title, message):
            if not self.modal:
                with dpg.mutex():
                    viewport_width = dpg.get_viewport_client_width()
                    viewport_height = dpg.get_viewport_client_height()
                    with dpg.window(label=title, no_close=True, modal=True) as modal_id:
                        dpg.add_text(message)
                        with dpg.group(horizontal=True):
                            dpg.add_button(
                                label="Ok",
                                width=-1,
                                user_data=(modal_id, True),
                                callback=lambda: dpg.delete_item(modal_id),
                            )

                dpg.split_frame()
                width = dpg.get_item_width(modal_id)
                height = dpg.get_item_height(modal_id)
                dpg.set_item_pos(modal_id, [viewport_width // 2 - width // 2, viewport_height // 2 - height // 2])
            else:
                print(f"DEV:ERROR:{title}:\t{message}\n\t\t\tCannot display message while file_dialog is in modal")

        def return_items():
            dpg.hide_item(self.tag)
            if self.callback is None:
                pass
            elif self.saving:
                self.callback((dpg.get_value("ex_file_name"), self.file_filter, os.getcwd()))
            else:
                self.callback(self.selected_files)
            self.selected_files.clear()
            reset_dir(default_path=self.default_path)
            self.callback = None

        def open_drive(sender, app_data, user_data):
            chdir(user_data)

        def open_file(sender, app_data, user_data):
            global last_click_time
            # Multi selection
            if dpg.is_key_down(dpg.mvKey_Control):
                if dpg.get_value(sender) is True:
                    self.selected_files.append(user_data[1])
                else:
                    self.selected_files.remove(user_data[1])
            # Single selection
            else:
                dpg.set_value(sender, False)

                current_time = time.time()
                if current_time - last_click_time < 0.5:  # adjust the time as needed
                    if user_data is not None and user_data[1] is not None:
                        if os.path.isdir(user_data[1]):
                            chdir(user_data[1])
                            if not self.saving:
                                dpg.set_value("ex_search", "")
                        elif os.path.isfile(user_data[1]):
                            self.selected_files.append(user_data[1])
                            return_items()
                            return user_data[1]
                last_click_time = current_time

        def _search():
            res = dpg.get_value("ex_search")
            reset_dir(default_path=os.getcwd(), file_name_filter=res)

        def _makedir(item, callback, parent="explorer", size=False):
            file_name = os.path.basename(item)

            creation_time = os.path.getctime(item)
            creation_time = time.ctime(creation_time)

            item_type = "Dir"

            item_size = get_file_size(item)

            kwargs_cell = {
                "callback": callback,
                "span_columns": True,
                "height": self.selec_height,
                "user_data": [file_name, os.path.join(os.getcwd(), file_name)],
            }

            with dpg.table_row(parent=parent):
                with dpg.group(horizontal=True):
                    if file_name.endswith((".png", ".jpg")):
                        dpg.add_image(self.img_picture)
                    elif item_type == "Dir":
                        dpg.add_image(self.img_mini_folder)
                    elif item_type == "File":
                        dpg.add_image(self.img_mini_document)

                    cell_name = dpg.add_selectable(label=file_name, **kwargs_cell)
                cell_time = dpg.add_selectable(label=creation_time, **kwargs_cell)
                cell_type = dpg.add_selectable(label=item_type, **kwargs_cell)
                cell_size = dpg.add_selectable(label=str(item_size), **kwargs_cell)

                if self.allow_drag is True:
                    drag_payload = dpg.add_drag_payload(parent=cell_name, payload_type=self.PAYLOAD_TYPE)
                dpg.bind_item_theme(cell_name, self.selec_alignt)
                dpg.bind_item_theme(cell_time, self.selec_alignt)
                dpg.bind_item_theme(cell_type, self.selec_alignt)
                dpg.bind_item_theme(cell_size, self.size_alignt)
                if self.allow_drag is True:
                    if file_name.endswith((".png", ".jpg")):
                        dpg.add_image(self.img_big_picture, parent=drag_payload)
                    elif item_type == "Dir":
                        dpg.add_image(self.img_folder, parent=drag_payload)
                    elif item_type == "File":
                        dpg.add_image(self.img_document, parent=drag_payload)

        def _makefile(item, callback, parent="explorer"):
            if self.file_filter == ".*" or item.endswith(self.file_filter):
                file_name = os.path.basename(item)

                creation_time = os.path.getctime(item)
                creation_time = time.ctime(creation_time)

                item_type = "File"

                item_size = get_file_size(item)
                kwargs_cell = {
                    "callback": callback,
                    "span_columns": True,
                    "height": self.selec_height,
                    "user_data": [file_name, os.path.join(os.getcwd(), file_name)],
                }

                with dpg.table_row(parent=parent):
                    with dpg.group(horizontal=True):
                        if file_name.endswith((".png", ".jpg")):
                            dpg.add_image(self.img_picture)
                        elif item_type == "Dir":
                            dpg.add_image(self.img_mini_folder)
                        elif item_type == "File":
                            dpg.add_image(self.img_mini_document)

                        cell_name = dpg.add_selectable(label=file_name, **kwargs_cell)
                    cell_time = dpg.add_selectable(label=creation_time, **kwargs_cell)
                    cell_type = dpg.add_selectable(label=item_type, **kwargs_cell)
                    cell_size = dpg.add_selectable(label=str(item_size), **kwargs_cell)

                    if self.allow_drag is True:
                        drag_payload = dpg.add_drag_payload(parent=cell_name, payload_type=self.PAYLOAD_TYPE)
                    dpg.bind_item_theme(cell_name, self.selec_alignt)
                    dpg.bind_item_theme(cell_time, self.selec_alignt)
                    dpg.bind_item_theme(cell_type, self.selec_alignt)
                    dpg.bind_item_theme(cell_size, self.size_alignt)
                    if self.allow_drag is True:
                        if file_name.endswith((".png", ".jpg")):
                            dpg.add_image(self.img_big_picture, parent=drag_payload)
                        elif item_type == "Dir":
                            dpg.add_image(self.img_folder, parent=drag_payload)
                        elif item_type == "File":
                            dpg.add_image(self.img_document, parent=drag_payload)

        def _back(sender, app_data, user_data):
            global last_click_time
            if dpg.is_key_down(dpg.mvKey_Control):
                dpg.set_value(sender, False)
            else:
                dpg.set_value(sender, False)
                current_time = time.time()
                if current_time - last_click_time < 0.5:
                    if not self.saving:
                        dpg.set_value("ex_search", "")
                    chdir("..")
                    last_click_time = 0
                last_click_time = current_time

        def filter_combo_selector(sender, app_data):
            filter_file = dpg.get_value(sender)
            self.file_filter = filter_file
            cwd = os.getcwd()
            reset_dir(default_path=cwd)

        def chdir(path):
            try:
                os.chdir(path)
                cwd = os.getcwd()
                reset_dir(default_path=cwd)
            except PermissionError as e:
                message_box(
                    "File dialog - PerimssionError",
                    f"Cannot open the folder because is a system folder or the access is denied\n\nMore info:\n{e}",
                )

        def reset_dir(file_name_filter=None, default_path=self.default_path):
            def internal():
                self.selected_files.clear()
                try:
                    dpg.configure_item("ex_path_input", default_value=os.getcwd())
                    _dir = os.listdir(default_path)
                    delete_table()

                    # Separate directories and files
                    dirs = [file for file in _dir if os.path.isdir(file)]
                    files = [file for file in _dir if os.path.isfile(file)]
                    self.dirs_only = self.saving

                    # 'special directory' that sends back to the other directory
                    with dpg.table_row(parent="explorer"):
                        dpg.add_selectable(label="..", callback=_back, span_columns=True, height=self.selec_height)

                        # dir list
                        for file in dirs:
                            if file_name_filter:
                                if dpg.get_value("ex_search") in file:
                                    _makedir(file, open_file)
                            else:
                                _makedir(file, open_file)

                        if not self.dirs_only:
                            for file in files:
                                if file_name_filter:
                                    if dpg.get_value("ex_search") in file:
                                        _makefile(file, open_file)
                                else:
                                    _makefile(file, open_file)

                # exceptions
                except FileNotFoundError:
                    print("DEV:ERROR: Invalid path : " + str(default_path))
                except Exception as e:
                    message_box(
                        "File dialog - Error", f"An unknown error has occured when listing the items, More info:\n{e}"
                    )

            internal()

        def get_directory_path(directory_name):
            try:
                directory_path = os.path.join(os.path.expanduser("~"), directory_name)
                os.listdir(directory_path)
            except FileNotFoundError:
                directory_path = glob(os.path.expanduser("~\\*\\" + directory_name))[0]
                try:
                    os.listdir(directory_path)
                except FileNotFoundError:
                    message_box("File dialog - Error", "Could not find the selected directory")
                    return "."
            return directory_path

        if dpg.does_item_exist(self.tag):
            dpg.delete_item(self.tag)
            with contextlib.suppress(SystemError):
                dpg.remove_alias(self.tag)

        # main file dialog header
        with dpg.window(
            label=self.title,
            tag=self.tag,
            no_resize=self.no_resize,
            show=False,
            modal=self.modal,
            width=self.width,
            height=self.height,
            min_size=self.min_size,
            no_collapse=True,
        ):
            info_px = 85 if self.saving else 55

            # horizontal group (shot_menu + dir_list)
            with dpg.group(horizontal=True):
                # shortcut menu
                with dpg.child_window(tag="shortcut_menu", width=200, show=self.show_shortcuts_menu, height=-info_px):
                    desktop = get_directory_path("Desktop")
                    downloads = get_directory_path("Downloads")
                    images = get_directory_path("Pictures")
                    documents = get_directory_path("Documents")
                    musics = get_directory_path("Music")
                    videos = get_directory_path("Videos")
                    current_directory = os.getcwd()

                    with dpg.group(horizontal=True):
                        dpg.add_image(self.img_desktop)
                        dpg.add_menu_item(label="Desktop", callback=lambda: chdir(desktop))
                    with dpg.group(horizontal=True):
                        dpg.add_image(self.img_downloads)
                        dpg.add_menu_item(label="Downloads", callback=lambda: chdir(downloads))
                    with dpg.group(horizontal=True):
                        dpg.add_image(self.img_picture_folder)
                        dpg.add_menu_item(label="Images", callback=lambda: chdir(images))
                    with dpg.group(horizontal=True):
                        dpg.add_image(self.img_document_folder)
                        dpg.add_menu_item(label="Documents", callback=lambda: chdir(documents))
                    with dpg.group(horizontal=True):
                        dpg.add_image(self.img_music_folder)
                        dpg.add_menu_item(label="Musics", callback=lambda: chdir(musics))
                    with dpg.group(horizontal=True):
                        dpg.add_image(self.img_videos)
                        dpg.add_menu_item(label="Videos", callback=lambda: chdir(videos))
                    with dpg.group(horizontal=True):
                        dpg.add_image(self.img_folder, width=16, height=16)
                        dpg.add_menu_item(label="Current Directory", callback=lambda: chdir(current_directory))
                    dpg.add_separator()

                    # i/e drives list
                    with dpg.group():
                        drives = _get_all_drives()
                        for drive in drives:
                            with dpg.group(horizontal=True):
                                dpg.add_image(self.img_hard_disk)
                                dpg.add_menu_item(label=drive, user_data=drive, callback=open_drive)

                # main explorer header
                with dpg.group():
                    with dpg.group(horizontal=True):
                        dpg.add_image_button(
                            self.img_refresh, tag="ex_refresh", callback=lambda: reset_dir(default_path=os.getcwd())
                        )
                        dpg.add_input_text(
                            hint="Path",
                            on_enter=True,
                            callback=on_path_enter,
                            default_value=os.getcwd(),
                            width=-1,
                            tag="ex_path_input",
                        )
                    if not self.saving:
                        with dpg.group(horizontal=True):
                            dpg.add_input_text(hint="Search files", callback=_search, tag="ex_search", width=-1)

                    # main explorer table header
                    with dpg.table(
                        tag="explorer",
                        height=-info_px,
                        width=-1,
                        resizable=True,
                        policy=dpg.mvTable_SizingStretchProp,
                        borders_innerV=True,
                        reorderable=True,
                        hideable=True,
                        sortable=True,
                        scrollX=True,
                        scrollY=True,
                    ):
                        iwow_name = 100
                        iwow_date = 50
                        iwow_type = 10
                        iwow_size = 10
                        dpg.add_table_column(label="Name", init_width_or_weight=iwow_name, tag="ex_name")
                        dpg.add_table_column(label="Date", init_width_or_weight=iwow_date, tag="ex_date")
                        dpg.add_table_column(label="Type", init_width_or_weight=iwow_type, tag="ex_type")
                        dpg.add_table_column(label="Size", init_width_or_weight=iwow_size, width=10, tag="ex_size")

            if self.saving:
                with dpg.group(horizontal=True):
                    window_width = dpg.get_item_width(self.tag)
                    input_text_width = int(self.width * 0.8)
                    spacer_width = (window_width - input_text_width) / 2 - 20
                    dpg.add_spacer(width=int(spacer_width))
                    dpg.add_input_text(hint="Save File As...", width=input_text_width, tag="ex_file_name")

            with dpg.group(horizontal=True):
                dpg.add_spacer(width=50)
                dpg.add_text("File type")
                dpg.add_combo(
                    items=[".*", ".png", ".jpg", ".jpeg", ".bmp"]
                    if self.file_filter != ".cresliant"
                    else [".cresliant"],
                    callback=filter_combo_selector,
                    default_value=self.file_filter,
                    width=-1,
                )
            with dpg.group(horizontal=True):
                dpg.add_spacer(width=int(self.width * 0.82))
                dpg.add_button(label="   OK   ", callback=return_items)
                dpg.add_button(label=" Cancel ", callback=lambda: dpg.hide_item(self.tag))

            if self.default_path == "cwd":
                chdir(os.getcwd())
            else:
                chdir(self.default_path)

        auto_align(self.tag, AlignmentType.Both)

    # high-level functions
    def show_file_dialog(self):
        self.start()
        dpg.show_item(self.tag)

    def change(self, callback, saving=False, file_filter=None):
        self.callback = callback
        self.saving = saving
        if file_filter:
            self.file_filter = file_filter
        else:
            self.file_filter = ".png"


fd = FileDialog(callback=None, default_path=os.curdir, allow_drag=False, file_filter=".png", multi_selection=False)
