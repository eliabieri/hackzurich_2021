import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:frontend/map_data_provider.dart';
import 'package:latlong2/latlong.dart';
import 'package:maps_launcher/maps_launcher.dart';

class AnomalyMarker extends Marker {
  final Anomaly anomaly;
  AnomalyMarker({Key? key, required this.anomaly})
      : super(
          width: 80.0,
          height: 80.0,
          point: LatLng(anomaly.lat, anomaly.lon),
          builder: (context) {
            return GestureDetector(
              onTap: () => showDialog(
                  context: context,
                  builder: (context) => Dialog(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            const SizedBox(
                              height: 20,
                            ),
                            Text(
                              "Possible failure",
                              style: Theme.of(context).textTheme.headline4,
                            ),
                            const SizedBox(
                              height: 5,
                            ),
                            Text(
                              "Detected on ${anomaly.detectedOn}",
                              style: Theme.of(context).textTheme.bodyText2,
                            ),
                            const SizedBox(
                              height: 20,
                            ),
                            Text(
                              "Severeness: ${anomaly.severeness}",
                              style: Theme.of(context).textTheme.headline6,
                            ),
                            const SizedBox(
                              height: 10,
                            ),
                            Text(
                              "Type: ${anomaly.type == 'INTERFERENCE' ? 'Packet loss due to interferences' : 'Possible damage on the antenna'}",
                              style: Theme.of(context).textTheme.headline6,
                              textAlign: TextAlign.center,
                            ),
                            const SizedBox(
                              height: 10,
                            ),
                            ElevatedButton(
                                child: const Text("Get directions"),
                                onPressed: () =>
                                    MapsLauncher.launchCoordinates(anomaly.lat, anomaly.lon)),
                            const SizedBox(
                              height: 20,
                            ),
                          ],
                        ),
                      )),
              child: FaIcon(anomaly.type == "INTERFERENCE"
                  ? FontAwesomeIcons.broadcastTower
                  : FontAwesomeIcons.waveSquare),
            );
          },
        );
}
