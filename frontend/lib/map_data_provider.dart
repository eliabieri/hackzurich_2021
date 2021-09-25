import 'dart:async';
import 'dart:convert';
import 'package:equatable/equatable.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class Anomaly extends Equatable {
  final double lat;
  final double lon;
  final String type;
  final double severeness;
  final int distanceOnTrack;
  final DateTime detectedOn;

  const Anomaly(
      {required this.lat,
      required this.lon,
      required this.type,
      required this.severeness,
      required this.distanceOnTrack,
      required this.detectedOn});

  @override
  List<Object> get props => [lat, lon, type, severeness, distanceOnTrack, detectedOn];
}

class MapDataProvider {
  StreamController<List<Anomaly>>? _controller;
  List<Anomaly> anomalies = [];

  MapDataProvider() {
    _controller = StreamController<List<Anomaly>>();
    Timer.periodic(const Duration(seconds: 1), (Timer t) => updateData());
  }

  Future<void> updateData() async {
    try {
      final resp = await http.get(Uri.parse("http://127.0.0.1:8000/anomalies"));
      final data = jsonDecode(resp.body) as Map<String, dynamic>;
      final newAnomalies = List<Map<String, dynamic>>.from((data["anomalies"] as List<dynamic>))
          .map((e) => Anomaly(
              lat: e["lat"],
              lon: e["lon"],
              type: e["type"],
              severeness: e["severeness"],
              distanceOnTrack: e["distanceOnTrack"],
              detectedOn: DateTime.parse(e["detectedOn"])))
          .toList();
      if (!listEquals(newAnomalies, anomalies)) {
        anomalies = newAnomalies;
        _controller?.add(anomalies);
      }
    } catch (e) {
      print(e);
    }
  }

  Stream<List<Anomaly>>? get mapDataStream => _controller?.stream;
}
