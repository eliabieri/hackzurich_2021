import 'dart:ui';

import 'package:animations/animations.dart';
import 'package:flutter/material.dart';
import 'package:future_progress_dialog/future_progress_dialog.dart';

Future<dynamic> showProgress(BuildContext context, Function future) async {
  await showModal(
    context: context,
    filter: ImageFilter.blur(sigmaX: 2, sigmaY: 2),
    builder: (context) => FutureProgressDialog(
      future(),
      progress:
          const CircularProgressIndicator(valueColor: AlwaysStoppedAnimation<Color>(Colors.black)),
    ),
  );
  return future;
}
