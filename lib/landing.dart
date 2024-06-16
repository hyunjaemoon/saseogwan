import 'package:flutter/material.dart';

class HomePage extends StatefulWidget {
  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  PageController _pageController = PageController();
  double _pageOffset = 0;

  @override
  void initState() {
    super.initState();
    _pageController.addListener(() {
      setState(() {
        _pageOffset = _pageController.page!;
      });
    });
  }

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // Animated background
          Positioned.fill(
            child: AnimatedBuilder(
              animation: _pageController,
              builder: (context, child) {
                return Transform.translate(
                  offset: Offset(_pageOffset * -100, 0),
                  child: child,
                );
              },
              child: Image.asset(
                'assets/background.png',
                fit: BoxFit.cover,
              ),
            ),
          ),
          // PageView
          PageView(
            controller: _pageController,
            children: [
              Container(
                  color: Colors.transparent,
                  child: Center(child: Text('Page 1'))),
              Container(
                  color: Colors.transparent,
                  child: Center(child: Text('Page 2'))),
              Container(
                  color: Colors.transparent,
                  child: Center(child: Text('Page 3'))),
            ],
          ),
        ],
      ),
    );
  }
}
