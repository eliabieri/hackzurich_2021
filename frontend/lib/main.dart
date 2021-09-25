import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:frontend/upload_dialog.dart';
import 'package:http/http.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'package:modal_bottom_sheet/modal_bottom_sheet.dart';

import 'map_data_provider.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  final siemensColor = const Color.fromRGBO(0, 153, 153, 1.0);

  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final mapData = MapDataProvider();
    return MaterialApp(
      title: "Siemens ZSL90 Predictive Maintenance",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(primaryColor: siemensColor),
      home: Scaffold(
        appBar: AppBar(
          title: const Text("Siemens ZSL90 Predictive Maintenance"),
          backgroundColor: siemensColor,
          actions: [
            Padding(
              padding: const EdgeInsets.only(right: 8.0),
              child: Builder(builder: (context) {
                return IconButton(
                  icon: const Icon(Icons.upload_file),
                  onPressed: () => showCupertinoModalBottomSheet(
                    context: context,
                    builder: (context) => const UploadData(),
                  ),
                );
              }),
            )
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
              return Stack(
                alignment: Alignment.center,
                children: [
                  FlutterMap(
                    options: MapOptions(
                      center: LatLng(47.32913856887063, 8.12325467579632),
                      zoom: 10.0,
                    ),
                    layers: [
                      TileLayerOptions(
                        urlTemplate: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                        subdomains: ['a', 'b', 'c'],
                      ),
                      MarkerLayerOptions(
                          markers: snapshot.data
                                  ?.map(
                                    (e) => Marker(
                                      width: 80.0,
                                      height: 80.0,
                                      point: LatLng(e.lat, e.lon),
                                      builder: (ctx) {
                                        final anomalyType = e.type;
                                        if ("INTERFERENCE" == anomalyType) {
                                          return const FaIcon(FontAwesomeIcons.broadcastTower);
                                        }
                                        return const FaIcon(FontAwesomeIcons.waveSquare);
                                      },
                                    ),
                                  )
                                  .toList() ??
                              []),
                    ],
                  ),
                  Positioned(
                    bottom: 20,
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
                  )
                ],
              );
            }),
      ),
    );
  }
}
