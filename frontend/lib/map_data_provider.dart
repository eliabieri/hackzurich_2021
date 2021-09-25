import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;

class Anomaly {
  final double lat;
  final double lon;
  final String type;
  final double severeness;

  const Anomaly(
      {required this.lat, required this.lon, required this.type, required this.severeness});
}

class MapDataProvider {
  StreamController<List<Anomaly>>? _controller;

  MapDataProvider() {
    _controller = StreamController<List<Anomaly>>();
    Timer.periodic(const Duration(seconds: 1), (Timer t) => updateData());
  }

  Future<void> updateData() async {
    final resp = await http.get(Uri.parse("http://127.0.0.1:8000/anomalies"));
    final data = jsonDecode(resp.body) as Map<String, dynamic>;
    final anomalies = List<Map<String, dynamic>>.from((data["anomalies"] as List<dynamic>))
        .map((e) =>
            Anomaly(lat: e["lat"], lon: e["lon"], type: e["type"], severeness: e["severeness"]))
        .toList();
    _controller?.add(anomalies);
  }

  Stream<List<Anomaly>>? get mapDataStream => _controller?.stream;
}
