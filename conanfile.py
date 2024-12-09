import traceback

from conan import ConanFile
from conan.tools.cmake import cmake_layout

from ue5_conan.build.build_plugin import UnrealPlugin
from ue5_conan.config.ue_project import configure_unreal_package
from ue5_conan.generator.build_generator import UnrealPluginToolchain
from ue5_conan.package.plugins import package_plugin


class PaperFlipbookWidgetConan(ConanFile):
    plugin_name = "PaperFlipbookWidget"
    name = "paper-flipbook-widget"
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
        configure_unreal_package(self)

    def layout(self):
        cmake_layout(self)    

    def generate(self):
        toolchain = UnrealPluginToolchain(self, self.plugin_name)
        toolchain.generate()
            
    def build(self):
        plugin = UnrealPlugin(self, self.plugin_name)
        plugin.build()

    def package(self):
        package_plugin(self)