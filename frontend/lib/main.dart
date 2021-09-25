import 'package:auto_size_text/auto_size_text.dart';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_picker/Picker.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:flutter_svg/svg.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:frontend/polyline.dart';
import 'package:frontend/upload_dialog.dart';
import 'package:frontend/widgets/marker.dart';
import 'package:latlong2/latlong.dart';
import 'package:modal_bottom_sheet/modal_bottom_sheet.dart';
import 'package:provider/provider.dart';

import 'map_data_provider.dart';

final mapData = MapDataProvider();

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  final siemensColor = const Color.fromRGBO(0, 153, 153, 1.0);

  final MapController _mapController = MapController();

  MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "Siemens ZSL90 Predictive Maintenance",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
          primaryColor: siemensColor,
          fontFamily: "Siemens",
          elevatedButtonTheme: ElevatedButtonThemeData(
              style: ButtonStyle(backgroundColor: MaterialStateProperty.all(siemensColor)))),
      home: Scaffold(
        appBar: AppBar(
          title: Column(
            children: [
              SvgPicture.asset(
                "assets/siemens-logo.svg",
                height: 20,
              ),
              const SizedBox(
                height: 5,
              ),
              Text("ZSL90 Predictive Maintenance Tool",
                  style: TextStyle(color: siemensColor, fontSize: 14)),
            ],
          ),
          backgroundColor: Colors.white,
          actions: [
            Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: Builder(builder: (context) {
                return IconButton(
                  icon: Icon(Icons.upload_file, color: siemensColor),
                  onPressed: () => showBarModalBottomSheet(
                      expand: false, context: context, builder: (context) => const UploadData()),
                );
              }),
            )
          ],
        ),
        floatingActionButton: Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            FloatingActionButton(
              heroTag: UniqueKey(),
              child: const Icon(Icons.zoom_out),
              backgroundColor: siemensColor,
              onPressed: () => _mapController.move(_mapController.center, _mapController.zoom - 1),
            ),
            const SizedBox(width: 10),
            FloatingActionButton(
              heroTag: UniqueKey(),
              child: const Icon(Icons.zoom_in),
              backgroundColor: siemensColor,
              onPressed: () => _mapController.move(_mapController.center, _mapController.zoom + 1),
            ),
          ],
        ),
        body: StreamBuilder(
            stream: mapData.mapDataStream,
            builder: (context, AsyncSnapshot<List<Anomaly>> snapshot) {
              if (ConnectionState.active != snapshot.connectionState) {
                return const Center(
                  child: CircularProgressIndicator(),
                );
              }
              if (snapshot.hasError) {
                return Center(child: Text(snapshot.error.toString()));
              }
              return ChangeNotifierProvider(
                  create: (_) => ValueNotifier<double>(0.0),
                  builder: (context, _) {
                    return Stack(
                      alignment: Alignment.center,
                      children: [
                        Consumer<ValueNotifier<double>>(builder: (context, minSeverity, _) {
                          return FlutterMap(
                            mapController: _mapController,
                            options: MapOptions(
                              center: LatLng(47.32913856887063, 8.12325467579632),
                              zoom: 11.0,
                            ),
                            layers: [
                              TileLayerOptions(
                                urlTemplate: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                                subdomains: ['a', 'b', 'c'],
                              ),
                              PolylineLayerOptions(polylines: [
                                Polyline(
                                    points: polylineTrack,
                                    color: Colors.deepPurple,
                                    strokeWidth: 3.0,
                                    isDotted: true)
                              ]),
                              MarkerLayerOptions(
                                  markers: snapshot.data
                                          ?.where(
                                              (element) => element.severeness >= minSeverity.value)
                                          .map((e) => AnomalyMarker(anomaly: e))
                                          .toList() ??
                                      []),
                            ],
                          );
                        }),
                        Positioned(
                          bottom: 20,
                          left: 20,
                          child: SizedBox(
                            height: 45,
                            width: 150,
                            child: Card(
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(15.0),
                              ),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: const [
                                  Text("Updating live"),
                                  SizedBox(
                                    width: 10,
                                  ),
                                  SpinKitThreeBounce(
                                    color: Colors.black,
                                    size: 10.0,
                                  )
                                ],
                              ),
                            ),
                          ),
                        ),
                        Consumer<ValueNotifier<double>>(builder: (context, minSeverity, _) {
                          return Positioned(
                              top: 30,
                              left: 30,
                              child: SizedBox(
                                  height: 45,
                                  width: 45,
                                  child: Card(
                                    color: siemensColor,
                                    shape: RoundedRectangleBorder(
                                      borderRadius: BorderRadius.circular(8.0),
                                    ),
                                    child: IconButton(
                                      onPressed: () => _showFilterPopup(context, minSeverity),
                                      icon: const FaIcon(FontAwesomeIcons.filter,
                                          color: Colors.white),
                                    ),
                                  )));
                        })
                      ],
                    );
                  });
            }),
      ),
    );
  }

  void _showFilterPopup(BuildContext context, ValueNotifier<double> minSeverity) {
    Picker(
        adapter: PickerDataAdapter<double>(
            pickerdata: List<double>.generate(10, (int index) => index / 10)),
        hideHeader: false,
        onConfirm: (Picker picker, List value) {
          minSeverity.value = picker.getSelectedValues().first;
        }).showModal(context);
  }
}
