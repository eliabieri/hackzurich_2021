import 'dart:async';
import 'dart:convert';
import 'package:equatable/equatable.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

class Anomaly extends Equatable {
  final double lat1;
  final double lon1;
  final double lat2;
  final double lon2;
  final bool peak;
  final String type;
  final double severeness;
  final int distanceOnTrack;
  final DateTime detectedOn;

  const Anomaly(
      {required this.lat1,
      required this.lon1,
      required this.lat2,
      required this.lon2,
      required this.peak,
      required this.type,
      required this.severeness,
      required this.distanceOnTrack,
      required this.detectedOn});

  @override
  List<Object> get props =>
      [lat1, lon1, lat2, lon2, peak, type, severeness, distanceOnTrack, detectedOn];
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
              lat1: e["lat1"],
              lon1: e["lon1"],
              lat2: e["lat2"],
              lon2: e["lon2"],
              peak: e["peak"],
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
