import 'package:intl/intl.dart';

class TFormatter {
  static String formatDate(DateTime? date, {String locale = 'ar'}) {
    date ??= DateTime.now();
    return DateFormat.yMMMMd(locale).format(date);
  }

  static String formatDateTime(DateTime? date, {String locale = 'ar'}) {
    date ??= DateTime.now();
    return DateFormat.yMMMd(locale).add_jm().format(date);
  }

  static String formatShortDate(DateTime? date) {
    date ??= DateTime.now();
    return DateFormat('yyyy-MM-dd').format(date);
  }

  static String timeAgo(DateTime date) {
    final diff = DateTime.now().difference(date);
    if (diff.inDays > 30) {
      return '${(diff.inDays / 30).floor()} شهر مضت';
    } else if (diff.inDays > 0) {
      return '${diff.inDays} يوم مضى';
    } else if (diff.inHours > 0) {
      return '${diff.inHours} ساعة مضت';
    } else if (diff.inMinutes > 0) {
      return '${diff.inMinutes} دقيقة مضت';
    } else {
      return 'الآن';
    }
  }
}
