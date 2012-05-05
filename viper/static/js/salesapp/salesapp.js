/*
 *   Viper POS
 *	salesapp.js
 *	contains backbone based mvc app.
 */
(function ($) {

	LineItem = Backbone.Model.extend({
		defaults: {
			slno: null,
			barcode: null,
			name: null,
			quantity: 0.0,
			mrp: 0.0,
			price: 0.0,
			discount: 0.0,
			subtotal: 0.0
		}
	});

	LineItemCollection = Backbone.Collection.extend({
		initialize: function (models, options) {
			this.bind("add", this.addLineItemRecord);
		},
		addLineItemRecord: function (item) {
			console.log(item);
			$('#totalItemsQuantity').text(''+this.length+'/0');
		}
	});

	OrderPayment = Backbone.Model.extend({
		defaults: {
			id: null,
			orderid: null,
			paymentdate: new Date(),
			paymenttype: 'Cash',
			paidamount: 0.0,
			description: 0.0
		}
	});

	OrderPaymentsCollection = Backbone.Collection.extend({});

	Order = Backbone.Model.extend({
		defaults: {
			id: null,
			orderno: 0,
			orderdate: new Date(),
			customerid: null,
			customername: '',
			lineItems: null,
			payments: null,
			orderamount: 0.0,
			paidamount: 0.0,
			isprinted: false
		}
	});

	OrdersCollection = Backbone.Collection.extend({
		initialize: function (models, options) {
			this.bind("add", this.addorderitem);
		},
		addorderitem: function (item) {
			//console.log(item.get('orderdate'));
			var tr = '<tr data-orderid="'+ item.get('id') +'">';
			tr += '<td>' + item.get('orderno') + '</td>';
			tr += '<td>' + item.get('customername') + '</td>';
			tr += '<td>' + item.get('orderamount') + '</td>';
			tr += '</tr>';
			$('#tblTodayOrders tbody').append(tr);
			
			$('#orderDate').html(item.get('orderdate'));
			$('#orderNumber').html(item.get('orderno'));
		}
	});

	window.SalesAppView = Backbone.View.extend({
		el: $("#sales-page"),
		initialize: function () {
			this.testCount = 1;
			this.lstOrders = new OrdersCollection;
			this.newOrder();
		},
		events: {
			"click #add-item": "addLineItem",
			"click #delete-item": "deleteLineItem",
			"click #print-order": "printOrder",
			"click #preview-order": "previewOrder",
			"click #new-order": "newOrder",
			"click #cancel-order": "cancelOrder",
			"click #checkout-order": "checkOutOrder",
		},
		addLineItem: function () {
			var item = new LineItem({
				slno: 1,
				name: 'test',
				barcode: '123',
				mrp: 12,
				quantity: 1,
				price: 10,
				discount: 0.0,
				subtotal: 10
			});
			this.currentOrder.get('lineItems').add(item);
		},
		deleteLineItem: function () {

		},
		newOrder: function () {
			this.currentOrder = new Order;
			this.currentOrder.set({'orderno':this.testCount++});
			this.currentOrder.set({'lineItems': new LineItemCollection(null, {
				view: this
			})});
			this.currentOrder.set({'payments': new OrderPaymentsCollection(null, {
				view: this
			})});
			this.lstOrders.add(this.currentOrder);
		},
		cancelOrder: function () {
			var items = this.currentOrder.get('lineItems');
			items.reset();
		},
		checkOutOrder: function () {

		},
		printOrder: function () {

		},
		previewOrder: function () {

		}
	});
	var salesappview = new SalesAppView;
})(jQuery);

