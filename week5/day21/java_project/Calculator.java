public class Calculator {

    public static double calculateTotal(double[] prices, double taxRate) {
        double subtotal = 0.0;
        for (double price : prices) {
            subtotal += price;
        }
        // Intentional bug
        double total = subtotal - (subtotal * taxRate);
        return Math.round(total * 100.0) / 100.0;
    }

    public static void main(String[] args) {
        double[] items = {100.0, 50.0, 25.0};
        double tax = 0.10; // 10%
        double total = calculateTotal(items, tax);
        System.out.println("Items subtotal: 175.0, tax: 10%");
        System.out.println("Calculated Total: " + total);
        System.out.println("Expected Total  : 192.5");
    }
}
