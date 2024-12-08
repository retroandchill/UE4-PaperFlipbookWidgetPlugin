from conan import ConanFile
from conan.tools.cmake import cmake_layout
from conan.tools.files import copy, rmdir
from glob import glob
import os
import subprocess
import re
import json
import shutil
    

class PaperFlipbookWidgetConan(ConanFile):
    name = "paperflipbookwidget"
    version = "1.0.0"
    license = "MIT"
    url = "https://github.com/HoussineMehnik/UE4-PaperFlipbookWidgetPlugin"
    description = "Paper flipbook widget allows you to display a flipbook asset in the UI."
    topics = "Unreal Engine", "User Interface", "Paper2D"
    settings = "os", "build_type", "compiler", "arch"
    options = {
        "ue_install_location": [None, "ANY"],
        "ue_version": [None, "ANY"],
        "platform": [None, "ANY"]
    }
    default_options = {
        "ue_base_dir": None,
        "ue_version": None,
        "platform": None,
    }
    exports_sources = "PaperFlipbookWidget.uplugin", "Config/*", "Content/*", "Resources/*", "Source/*"

    def config_options(self):
        if self.options.ue_install_location != None:
            del self.options.ue_version

    def configure(self):
        if self.options.ue_install_location == None:
            if self.settings.os == "Windows":
                epic_games_path = os.path.join(os.environ["ProgramFiles"], "Epic Games")
            elif self.settings.os == "macOS":
                epic_games_path = os.path.join("Users", "Shared", "Epic Games")
            else:
                raise FileNotFoundError(f"Can't detect the engine installation for the following platform: {self.settings.os}")
            
            if self.options.ue_version == None:
                versions = []
                for entry in os.scandir(epic_games_path):
                    if not entry.is_dir():
                        continue
                    
                    match = re.match(r'UE_(\d+\.\d+)', entry.name)
                    if match is not None:
                        versions.append(match.group(1))
                
                if len(versions) == 0:
                    raise FileNotFoundError(f"Could not find engine installation in directory: {epic_games_path}")

                versions.sort(reverse=True)
                self.options.ue_version = versions[0]
                
            self.options.ue_install_location = os.path.join(epic_games_path, f"UE_{self.options.ue_version}")

        if self.options.platform == None:
            if self.settings.os == "Windows":
                if self.settings.arch == "x86_64":
                    self.options.platform = "Win64"
                elif self.settings.arch == "x86":
                    self.options.platfrom = "Win32"
                else:
                    raise ValueError(f"Invalid windows architecture: {self.settings.arch}")        

    def layout(self):
        cmake_layout(self)    

    def generate(self):
        templates_path = os.path.join(str(self.options.ue_install_location), 'Templates', 'TP_Blank')
        temp_project_folder = os.path.join(self.build_folder, "Build")
        copy(self, "*", dst=temp_project_folder, src=templates_path)
        
        plugins_directory = os.path.join(temp_project_folder, "Plugins")
        target_plugin_directory = os.path.join(plugins_directory, "PaperFlipbookWidget")
        copy(self, "*", dst=target_plugin_directory, src=self.source_folder)

        uproject_file = os.path.join(temp_project_folder, 'TP_Blank.uproject')
        with open(uproject_file, 'r') as f:
            content = json.load(f)

        content['EngineAssociation'] = '5.5'
        content['Plugins'].append({
            'Name': 'PaperFlipbookWidget',
            'Enabled': True
        })

        with open(uproject_file, 'w') as f:
            json.dump(content, f, indent=4)
            
    def build(self):
        build_tool_folder = os.path.join(str(self.options.ue_install_location), "Engine", "Binaries", "DotNet", "UnrealBuildTool")
        if self.settings.os == "Windows":
            script_path = os.path.join(build_tool_folder, "UnrealBuildTool.exe")
        else:
            raise ValueError("Build platform not supported")

        temp_project_folder = os.path.join(self.build_folder, "Build")
        uproject_file = glob(os.path.join(temp_project_folder, "*.uproject"))
        if len(uproject_file) != 1:
            raise FileNotFoundError("Could not resolve uproject file")
        project_path = uproject_file[0]
        base_cmd = [script_path, f'-Project={project_path}', "TP_BlankEditor", str(self.options.platform), "Development"]
        subprocess.run(base_cmd)

        plugins_directory = os.path.join(temp_project_folder, "Plugins")
        target_plugin_directory = os.path.join(plugins_directory, "PaperFlipbookWidget")
        copy(self, "*", dst=os.path.join(self.build_folder, "Binaries"), src=os.path.join(target_plugin_directory, "Binaries"))
        copy(self, "*", dst=os.path.join(self.build_folder, "Intermediate"), src=os.path.join(target_plugin_directory, "Intermediate"))
        rmdir(self, temp_project_folder)


    def package(self):
        copy(self, 'LICENSE', dst=self.package_folder, src=self.source_folder)
        copy(self, '*.uplugin', dst=self.package_folder, src=self.source_folder)
        src_folders = ['Config', 'Resources', 'Source']
        for folder in src_folders:
            copy(self, '*', dst=os.path.join(self.package_folder, folder), src=os.path.join(self.source_folder, folder))
        build_folders = ['Binaries', 'Intermediate']
        for folder in build_folders:
            copy(self, '*', dst=os.path.join(self.package_folder, folder), src=os.path.join(self.build_folder, folder))