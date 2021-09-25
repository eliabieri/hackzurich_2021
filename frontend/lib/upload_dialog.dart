import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter_styled_toast/flutter_styled_toast.dart';
import 'package:frontend/utils.dart';
import 'package:http/http.dart' as http;

class UploadData extends StatelessWidget {
  const UploadData({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return ListView(shrinkWrap: true, padding: const EdgeInsets.all(30), children: [
      Text(
        "Upload new data",
        style: Theme.of(context).textTheme.headline4,
      ),
      const SizedBox(
        height: 20,
      ),
      const Text("Choose events.csv, disruptions.csv and rssi.csv"),
      const SizedBox(height: 40),
      ElevatedButton(
          onPressed: () async {
            final result = await FilePicker.platform.pickFiles(
              type: FileType.custom,
              allowMultiple: true,
              dialogTitle: "Choose events.csv, disruptions.csv and rssi.csv",
              withReadStream: true,
              allowedExtensions: ['csv'],
            );
            await showProgress(context, () => uploadData(result)).then((value) {
              showToast(
                "Successfully uploaded data. Analysis in progress",
                context: context,
                backgroundColor: Colors.green,
                duration: const Duration(seconds: 4),
              );
              Navigator.of(context).pop();
            }).catchError((error) {
              print("Caught error");
              showToast("An error occured: $error",
                  context: context,
                  duration: const Duration(seconds: 4),
                  backgroundColor: Colors.red);
            });
          },
          child: const Text("Add data files"))
    ]);
  }

  Future<void> uploadData(FilePickerResult? filePickerResult) async {
    if (null == filePickerResult) {
      return Future.error("filePickerResult is null");
    }

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse("http://127.0.0.1:8000/data"),
      );
      Map<String, String> headers = {"Content-type": "multipart/form-data"};
      final events = filePickerResult.files.firstWhere((element) => "events.csv" == element.name);
      final rssi = filePickerResult.files.firstWhere((element) => "rssi.csv" == element.name);
      final disruptions =
          filePickerResult.files.firstWhere((element) => "disruptions.csv" == element.name);
      request.files.addAll([
        http.MultipartFile(
          'events',
          events.readStream!,
          events.size,
          filename: events.name,
        ),
        http.MultipartFile(
          'rssi',
          rssi.readStream!,
          rssi.size,
          filename: rssi.name,
        ),
        http.MultipartFile(
          'disruptions',
          disruptions.readStream!,
          disruptions.size,
          filename: disruptions.name,
        ),
      ]);
      request.headers.addAll(headers);
      var result = await request.send();
      if (result.statusCode != 200) {
        throw Exception("Status code is not 200. Got ${result.statusCode}");
      }
    } catch (e, stackTrace) {
      print("Error while uploading: $e");
      return Future.error(e, stackTrace);
    }
  }
}
