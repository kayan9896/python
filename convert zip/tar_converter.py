import os
import tarfile
import zipfile
import shutil
import tempfile
import subprocess
from pathlib import Path
import time


class TarConverter:
    def __init__(self, tar_path, output_path=None, verbose=False, progress_callback=None):
        self.tar_path = tar_path
        self.output_path = output_path
        self.verbose = verbose
        self.progress_callback = progress_callback or (lambda status, progress, message: None)

    def _extract_tar_to_temp(self):
        """Extract tar file to a temporary directory with progress reporting"""
        temp_dir = tempfile.mkdtemp()
        self._log(f"Extracting to temporary directory: {temp_dir}")

        self.progress_callback("extracting", 5, "Analyzing tar file...")

        try:
            with tarfile.open(self.tar_path, 'r:*') as tar:
                members = tar.getmembers()
                total_size = sum(m.size for m in members)
                extracted_size = 0

                self.progress_callback("extracting", 10, f"Extracting {len(members)} files...")

                for i, member in enumerate(members):
                    tar.extract(member, path=temp_dir)
                    extracted_size += member.size
                    progress = 10 + int((extracted_size / total_size) * 40)  # 10-50% of total progress
                    self.progress_callback("extracting", progress, f"Extracted {i+1}/{len(members)} files")
        except tarfile.ReadError as e:
            self._log(f"Warning: Error reading tar file: {e}")
            self._log("Attempting alternative extraction method...")
            self.progress_callback("extracting", 15, "Using alternative extraction method...")
            try:
                # Try using external tar command as fallback
                result = subprocess.run(['tar', '-xf', self.tar_path, '-C', temp_dir],
                                      stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if result.returncode != 0:
                    self._log(f"External tar extraction failed: {result.stderr.decode()}")
                    self.progress_callback("extracting", 20, "External tar extraction failed, trying anyway...")
                else:
                    self.progress_callback("extracting", 50, "Extraction completed with external tar")
            except Exception as e:
                self._log(f"Alternative extraction failed: {e}")
                self.progress_callback("extracting", 20, f"Alternative extraction failed: {str(e)}")

        return temp_dir

    def list_contents(self):
        """List contents of the tar file in a hierarchical structure"""
        try:
            file_tree = []
            with tarfile.open(self.tar_path, 'r:*') as tar:
                for member in tar.getmembers():
                    # Get file info
                    info = {
                        'name': os.path.basename(member.name),
                        'path': member.name,
                        'type': 'directory' if member.isdir() else 'file',
                        'size': member.size if not member.isdir() else 0,
                        'mtime': member.mtime,
                    }
                    file_tree.append(info)

            return self._build_tree_structure(file_tree)
        except tarfile.ReadError as e:
            # Fallback for corrupted tar files
            try:
                result = subprocess.run(['tar', '-tf', self.tar_path],
                                     stderr=subprocess.PIPE, stdout=subprocess.PIPE)
                if result.returncode == 0:
                    lines = result.stdout.decode().splitlines()
                    file_tree = []
                    for line in lines:
                        line = line.strip()
                        info = {
                            'name': os.path.basename(line) or line,
                            'path': line,
                            'type': 'directory' if line.endswith('/') else 'file',
                            'size': 0,  # Can't get size from command output
                            'mtime': 0,  # Can't get time from command output
                        }
                        file_tree.append(info)
                    return self._build_tree_structure(file_tree)
                else:
                    raise Exception(f"Failed to list contents: {result.stderr.decode()}")
            except Exception as e2:
                raise Exception(f"Error reading tar file: {e} and fallback failed: {e2}")

    def _build_tree_structure(self, file_list):
        """Convert flat file list to hierarchical tree structure"""
        tree = []
        dirs = {}

        # First pass: create all directories
        for item in file_list:
            if item['type'] == 'directory':
                dirs[item['path']] = {
                    'name': item['name'],
                    'path': item['path'],
                    'type': 'directory',
                    'children': []
                }

        # Second pass: add files and link to parent directories
        for item in file_list:
            if item['type'] == 'file':
                # Build the node for this file
                node = {
                    'name': item['name'],
                    'path': item['path'],
                    'type': 'file',
                    'size': item['size'],
                }

                # Find parent directory
                parent_path = os.path.dirname(item['path'])
                if parent_path == '':
                    tree.append(node)  # Root level file
                else:
                    # Ensure parent exists
                    if parent_path not in dirs:
                        # Create parent directories that were implicit
                        dirs[parent_path] = {
                            'name': os.path.basename(parent_path),
                            'path': parent_path,
                            'type': 'directory',
                            'children': []
                        }
                    dirs[parent_path]['children'].append(node)

        # Third pass: link directories to parent directories
        for path, dir_node in dirs.items():
            parent_path = os.path.dirname(path)
            if parent_path == '':
                tree.append(dir_node)  # Root level directory
            else:
                # Ensure parent exists
                if parent_path in dirs:
                    dirs[parent_path]['children'].append(dir_node)

        return tree

    def _log(self, message):
        if self.verbose:
            print(message)

    def convert_to_zip(self, output_path=None):
        """Convert tar to zip format with progress reporting"""
        if output_path is None:
            output_path = self.output_path or f"{os.path.splitext(self.tar_path)[0]}.zip"

        # Extract tar first (extracts to 50% progress)
        temp_dir = self._extract_tar_to_temp()

        try:
            self._log(f"Creating ZIP file: {output_path}")
            self.progress_callback("zipping", 50, "Starting ZIP compression...")

            # Get total files for progress tracking
            total_files = sum([len(files) for _, _, files in os.walk(temp_dir)])
            processed_files = 0

            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        self._log(f"Adding: {arcname}")
                        zipf.write(file_path, arcname)

                        processed_files += 1
                        progress = 50 + int((processed_files / total_files) * 50)  # 50-100% of total progress
                        self.progress_callback("zipping", progress, f"Compressed {processed_files}/{total_files} files")

            self.progress_callback("complete", 100, f"Successfully converted to ZIP: {output_path}")
            print(f"Successfully converted to ZIP: {output_path}")

        except Exception as e:
            print(f"Error creating ZIP file: {e}")
            self.progress_callback("failed", 0, f"Error creating ZIP file: {str(e)}")

            try:
                # Fallback to shutil method
                self._log("Trying alternative ZIP creation method...")
                self.progress_callback("zipping", 55, "Using alternative ZIP method...")

                base_name = os.path.splitext(output_path)[0]
                shutil.make_archive(base_name, 'zip', temp_dir)

                self.progress_callback("complete", 100, f"Successfully converted to ZIP using alternative method")
                print(f"Successfully converted to ZIP using alternative method: {output_path}")

            except Exception as e2:
                print(f"Alternative ZIP creation failed: {e2}")
                self.progress_callback("failed", 0, f"Alternative ZIP creation failed: {str(e2)}")
                raise
        finally:
            shutil.rmtree(temp_dir)

        return output_path

    def convert_to_7z(self, output_path=None):
        """Convert tar to 7z format with progress reporting"""
        if output_path is None:
            output_path = self.output_path or f"{os.path.splitext(self.tar_path)[0]}.7z"

        # Extract tar first (extracts to 50% progress)
        temp_dir = self._extract_tar_to_temp()

        try:
            try:
                # Try using py7zr library
                import py7zr
                self._log(f"Creating 7z file using py7zr: {output_path}")
                self.progress_callback("compressing", 50, "Starting 7z compression...")

                with py7zr.SevenZipFile(output_path, mode='w') as archive:
                    # Register a callback for progress
                    total_files = sum([len(files) for _, _, files in os.walk(temp_dir)])
                    processed_files = 0

                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            archive.write(file_path, arcname)

                            processed_files += 1
                            progress = 50 + int((processed_files / total_files) * 50)  # 50-100% of total progress
                            self.progress_callback("compressing", progress, f"Compressed {processed_files}/{total_files} files")

                self.progress_callback("complete", 100, f"Successfully converted to 7z")
                print(f"Successfully converted to 7z: {output_path}")

            except ImportError:
                # Fall back to 7z command line tool
                self._log("py7zr not found, trying 7z command line tool...")
                self.progress_callback("compressing", 55, "Using external 7z tool...")

                result = subprocess.run(['7z', 'a', output_path, f"{temp_dir}/*"],
                                      stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                      shell=True)  # Use shell for wildcard expansion

                if result.returncode == 0:
                    self.progress_callback("complete", 100, f"Successfully converted to 7z")
                    print(f"Successfully converted to 7z: {output_path}")
                else:
                    error_msg = f"Error creating 7z file: {result.stderr.decode()}"
                    self.progress_callback("failed", 0, error_msg)
                    print(error_msg)
                    print("Please install py7zr ('pip install py7zr') or 7z command line tool.")
                    raise Exception("7z creation failed")
        except Exception as e:
            print(f"Error creating 7z file: {e}")
            self.progress_callback("failed", 0, f"Error creating 7z file: {str(e)}")
            raise
        finally:
            shutil.rmtree(temp_dir)

        return output_path

    def convert_to_rar(self, output_path=None):
        """Convert tar to rar format with progress reporting"""
        if output_path is None:
            output_path = self.output_path or f"{os.path.splitext(self.tar_path)[0]}.rar"

        # Extract tar first (extracts to 50% progress)
        temp_dir = self._extract_tar_to_temp()

        try:
            self._log(f"Creating RAR file: {output_path}")
            self.progress_callback("compressing", 50, "Starting RAR compression...")

            try:
                # Try to find rar command
                result = subprocess.run(['rar', 'a', output_path, f"{temp_dir}/*"],
                                      stderr=subprocess.PIPE, stdout=subprocess.PIPE,
                                      shell=True)  # Use shell for wildcard expansion

                # Simulate progress since RAR doesn't provide it through command line
                for progress in range(50, 100, 5):
                    if result.returncode != 0:  # Break if process already failed
                        break
                    self.progress_callback("compressing", progress, f"Compressing with RAR...")
                    time.sleep(0.5)

                if result.returncode == 0:
                    self.progress_callback("complete", 100, f"Successfully converted to RAR")
                    print(f"Successfully converted to RAR: {output_path}")
                else:
                    error_msg = f"Error creating RAR file: {result.stderr.decode()}"
                    self.progress_callback("failed", 0, error_msg)
                    print(error_msg)
                    print("Please install RAR command line tool (WinRAR or unrar).")
                    raise Exception("RAR creation failed")
            except FileNotFoundError:
                error_msg = "RAR command not found. Please install WinRAR or unrar."
                self.progress_callback("failed", 0, error_msg)
                print(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            print(f"Error creating RAR file: {e}")
            self.progress_callback("failed", 0, f"Error creating RAR file: {str(e)}")
            raise
        finally:
            shutil.rmtree(temp_dir)

        return output_path