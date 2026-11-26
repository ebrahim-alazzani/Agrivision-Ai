import 'dart:ui';
import 'package:flutter/material.dart';
import '../../theme/agri_colors.dart';

class AgriTextField extends StatefulWidget {
  final TextEditingController? controller;
  final String label;
  final String? hint;
  final IconData? prefixIcon;
  final Widget? suffixIcon;
  final bool obscureText;
  final TextInputType keyboardType;
  final String? Function(String?)? validator;
  final void Function(String)? onChanged;
  final int maxLines;
  final bool enabled;
  final bool readOnly;

  const AgriTextField({
    super.key,
    this.controller,
    required this.label,
    this.hint,
    this.prefixIcon,
    this.suffixIcon,
    this.obscureText = false,
    this.keyboardType = TextInputType.text,
    this.validator,
    this.onChanged,
    this.maxLines = 1,
    this.enabled = true,
    this.readOnly = false,
  });

  @override
  State<AgriTextField> createState() => _AgriTextFieldState();
}

class _AgriTextFieldState extends State<AgriTextField> {
  final FocusNode _focusNode = FocusNode();
  bool _isFocused = false;

  @override
  void initState() {
    super.initState();
    _focusNode.addListener(() {
      setState(() {
        _isFocused = _focusNode.hasFocus;
      });
    });
  }

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          widget.label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 13,
            color: isDark ? AgriColors.darkText : AgriColors.lightText,
            fontFamily: 'Cairo',
          ),
        ),
        const SizedBox(height: 6),
        AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            boxShadow: _isFocused
                ? [
                    BoxShadow(
                      color: AgriColors.emerald.withValues(alpha: isDark ? 0.35 : 0.25),
                      blurRadius: 16,
                      offset: const Offset(0, 4),
                    ),
                  ]
                : [],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(16),
            child: BackdropFilter(
              filter: ImageFilter.blur(sigmaX: 16, sigmaY: 16),
              child: Container(
                decoration: BoxDecoration(
                  color: isDark
                      ? const Color(0xFF12171F).withValues(alpha: 0.78)
                      : Colors.white.withValues(alpha: 0.82),
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(
                    color: _isFocused
                        ? AgriColors.emerald
                        : (isDark
                            ? Colors.white.withValues(alpha: 0.12)
                            : Colors.black.withValues(alpha: 0.08)),
                    width: _isFocused ? 1.5 : 1.1,
                  ),
                ),
                child: TextFormField(
                  controller: widget.controller,
                  focusNode: _focusNode,
                  obscureText: widget.obscureText,
                  keyboardType: widget.keyboardType,
                  validator: widget.validator,
                  onChanged: widget.onChanged,
                  maxLines: widget.maxLines,
                  enabled: widget.enabled,
                  readOnly: widget.readOnly,
                  style: TextStyle(
                    color: isDark ? AgriColors.darkText : AgriColors.lightText,
                    fontSize: 14,
                    fontFamily: 'Cairo',
                  ),
                  decoration: InputDecoration(
                    hintText: widget.hint,
                    hintStyle: TextStyle(
                      color: isDark ? AgriColors.darkMuted : AgriColors.lightMuted,
                      fontSize: 13,
                      fontFamily: 'Cairo',
                    ),
                    filled: false,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                    border: InputBorder.none,
                    enabledBorder: InputBorder.none,
                    focusedBorder: InputBorder.none,
                    errorBorder: InputBorder.none,
                    prefixIcon: widget.prefixIcon != null
                        ? Icon(
                            widget.prefixIcon,
                            color: _isFocused
                                ? AgriColors.emerald
                                : (isDark ? AgriColors.darkMuted : AgriColors.lightMuted),
                            size: 20,
                          )
                        : null,
                    suffixIcon: widget.suffixIcon,
                  ),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
