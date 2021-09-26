import 'package:animate_do/animate_do.dart';
import 'package:flutter/material.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_svg/svg.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:frontend/map_data_provider.dart';
import 'package:latlong2/latlong.dart';
import 'package:maps_launcher/maps_launcher.dart';
import 'package:timeago/timeago.dart' as timeago;

Color colorFromSeverity(double severity) {
  if (severity < 0.4) {
    return Colors.grey.shade300;
  }
  if (severity < 0.7) {
    return Colors.yellow;
  }
  return Colors.red;
}

Color colorFromSeverityPolyline(double severity) {
  if (severity < 0.4) {
    return Colors.black;
  }
  if (severity < 0.7) {
    return Colors.yellow;
  }
  return Colors.red;
}

class AnomalyMarker extends Marker {
  final Anomaly anomaly;
  AnomalyMarker({Key? key, required this.anomaly})
      : super(
          width: 80.0,
          height: 80.0,
          point: LatLng(anomaly.lat1, anomaly.lon1),
          builder: (context) {
            return GestureDetector(
              onTap: () => showDialog(
                  context: context,
                  builder: (context) => Dialog(
                        child: Container(
                          width: 300,
                          padding: const EdgeInsets.only(left: 20.0),
                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const SizedBox(
                                height: 20,
                              ),
                              Text(
                                "Possible failure",
                                style: Theme.of(context)
                                    .textTheme
                                    .headline3
                                    ?.copyWith(color: colorFromSeverity(anomaly.severeness)),
                              ),
                              const SizedBox(
                                height: 10,
                              ),
                              Text(
                                "Detected: ${timeago.format(anomaly.detectedOn)}",
                                style: Theme.of(context).textTheme.bodyText2,
                              ),
                              const Divider(
                                thickness: 2,
                                endIndent: 20,
                                height: 40,
                              ),
                              Text(
                                "Distance: ${anomaly.distanceOnTrack}m",
                                style: Theme.of(context).textTheme.bodyText2,
                              ),
                              const SizedBox(
                                height: 10,
                              ),
                              Text(
                                "Severity: ${anomaly.severeness.toStringAsFixed(1)}",
                                style: Theme.of(context).textTheme.bodyText2,
                              ),
                              const SizedBox(
                                height: 10,
                              ),
                              Text(
                                "Type: ${anomaly.type == 'INTERFERENCE' ? 'Packet loss due to interferences' : 'Possible damage on the antenna'}",
                                style: Theme.of(context).textTheme.bodyText2,
                                textAlign: TextAlign.center,
                              ),
                              const SizedBox(
                                height: 25,
                              ),
                              ElevatedButton(
                                  child: const Text("Get directions"),
                                  onPressed: () =>
                                      MapsLauncher.launchCoordinates(anomaly.lat1, anomaly.lon1)),
                              const SizedBox(
                                height: 20,
                              ),
                            ],
                          ),
                        ),
                      )),
              child: Center(
                child: SizedBox(
                  width: 45,
                  child: FadeIn(
                    duration: const Duration(milliseconds: 900),
                    delay: const Duration(milliseconds: 400),
                    child: Card(
                      shape: const CircleBorder(),
                      color: colorFromSeverity(anomaly.severeness),
                      elevation: 15,
                      child: Center(
                        child: Padding(
                          padding: const EdgeInsets.all(6.0),
                          child: SvgPicture.asset(anomaly.type == "INTERFERENCE"
                              ? "assets/interference.svg"
                              : "assets/broken.svg"),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            );
          },
        );
}
