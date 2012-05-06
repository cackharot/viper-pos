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
		},
		initialize: function (model, options) {
			this.bind("change", this.updateUI);
		},
		updateUI: function () {
			var barcode = this.get('barcode');
			var name = this.get('name');
			var quantity = this.get('quantity');
			var mrp = this.get('mrp');
			var price = this.get('price');
			var subtotal = Math.ceil(price * quantity);

			this.set({
				'subtotal': subtotal
			})

			var $tr = $('tr[data-barcode=' + barcode + ']', $('#tblOrderLineItems tbody'));

			if ($tr.length > 0) {
				$('.n', $tr).text(name);
				$('.p', $tr).text(price);
				$('.q', $tr).text(quantity);
				$('.st', $tr).text(subtotal);
			}
		}
	});

	LineItemCollection = Backbone.Collection.extend({
		model: LineItem,
		url: '/sales/savelineitems',
		initialize: function (models, options) {
			this.bind("add", this.addLineItemRecord);
			this.bind("change", this.updateTotal);
			this.bind("reset", this.resetRecords);
		},
		addLineItemRecord: function (item) {
			var compiled = _.template($('#tpl-lineitem').html());
			var tr = compiled({
				'item': item
			});
			$('#tblOrderLineItems tbody').prepend(tr);
			this.updateTotal();
		},
		updateTotal: function () {
			var qas = this.getQAS();
			$('#totalAmount').text(qas.totalAmount);
			$('#savingsAmount').text(qas.savings);
			$('#totalItemsQuantity').text(qas.totalItems + '/' + qas.totalQuantity);
		},
		getQAS: function () {
			var totalItems = 0,
				totalQuantity = 0,
				amt = 0,
				savings = 0;

			for (i = 0; i < this.length; i++) {
				var barcode = this.at(i).get('barcode');
				var price = this.at(i).get('price');
				var quantity = this.at(i).get('quantity');
				var mrp = this.at(i).get('mrp');
				var sbt = this.at(i).get('subtotal');
				//var sbt = Math.ceil(price*quantity);
				if (!barcode.startsWith('.')) {
					totalQuantity += quantity;
					totalItems++;
				}

				amt += sbt;
				savings += ((mrp * quantity) - sbt);
			}

			totalQuantity = totalQuantity.toFixed(2);
			amt = Math.ceil(amt);
			savings = Math.ceil(savings);
			return {
				totalItems: totalItems,
				totalQuantity: totalQuantity,
				totalAmount: amt,
				savings: savings
			};
		},
		resetRecords: function () {
			$('#tblOrderLineItems tbody tr').each(function () {
				$(this).remove();
			});
			$('#totalAmount').text(0.0);
			$('#savingsAmount').text(0.0);
			$('#totalItemsQuantity').text('0/0');
		},
		hideUI: function (callback) {
			$('#tblOrderLineItems tbody').fadeOut('slow', function (e) {
				if (callback) callback();
			});
		},
		showUI: function (callback) {
			$('#tblOrderLineItems tbody').fadeIn('slow', function () {
				if (callback) callback();
			});
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

	OrderPaymentsCollection = Backbone.Collection.extend({
		model: OrderPayment,
	});

	Order = Backbone.Model.extend({
		urlRoot: '/sales/saveorder',
		defaults: {
			id: null,
			orderno: 0,
			orderdate: new Date(),
			customerid: null,
			customername: '',
			lineItems: new LineItemCollection(),
			payments: new OrderPaymentsCollection(),
			isprinted: false
		},
		getOrderAmount: function () {
			return this.get('lineItems').reduce(function (m, x) {
				return m + x.get('subtotal');
			}, 0);
		},
		getPaidAmount: function () {
			return this.get('payments').reduce(function (m, x) {
				return m + x.get('paidamount');
			}, 0);
		}
	});

	OrdersCollection = Backbone.Collection.extend({
		model: Order,
		initialize: function (models, options) {
			this.bind("add", this.addorderitem);
			this.bind("remove", this.removeorderitem);
			this.bind("change", this.updateorderitem);
		},
		addorderitem: function (item) {
			if (!item) return;
			var compiled = _.template($('#tpl-todayorderitem').html());
			var tr = compiled({
				'item': item
			});

			$('#tblTodayOrders tbody').prepend(tr);
		},
		removeorderitem: function (item) {
			if (!item) return;
			var orderid = item.get('orderid');
			var $tr = $('tr[data-orderid=' + orderid + ']', $('#tblTodayOrders tbody'));
			if ($tr.length > 0) $tr.remove();
		},
		updateorderitem: function (orderid) {
			if (!orderid) return;
			var item = this.find(function (x) {
				return x.get('orderid') == orderid;
			});
			if (item) {
				var orderno = item.get('orderno');
				var cname = item.get('customername');
				var amt = item.getOrderAmount();

				var $tr = $('tr[data-orderid="' + orderid + '"]', $('#tblTodayOrders tbody'));
				if ($tr.length > 0) {
					$('.o', $tr).text(orderno);
					$('.c', $tr).text(cname);
					$('.a', $tr).text(Math.ceil(amt).toFixed(2));
				}
			}
		},
		resetUI: function () {
			$('#tblTodayOrders tbody tr').each(function () {
				$(this).remove();
			});
		}
	});

	remote = (function () {
		var neworderurl = '/sales/neworder';
		var searchitemurl = '/sales/searchitem';
		return {
			newOrder: function (callback) {
				var order = {};
				$.post(neworderurl, null, function (data) {
					if (typeof (data) == "string") data = eval('(' + data + ')');
					order = data;
					if (callback) callback(data);
				}, 'json');
				return order;
			},
			searchItem: function (barcode, callback) {
				$.post(searchitemurl, {
					'barcode': barcode
				}, function (data) {
					if (typeof (data) == "string") data = eval('(' + data + ')');
					if (callback) callback(data);
				}, 'json');
			}
		};
	})();

	window.SalesAppView = Backbone.View.extend({
		el: $("#sales-page"),
		model: null,
		initialize: function () {
			this.lstOrders = new OrdersCollection;
			this.refreshOrders();
		},
		render: function () {
			var item = this.model;
			var odate = new Date(item.get('orderdate'));
			$('#orderDate').html(odate.toString('dd/mm/yyyy HH:MM tt'));
			$('#orderNumber').html(item.get('orderno'));
		},
		events: {
			"click #add-item": "addLineItem",
			"click #delete-item": "deleteLineItem",
			"click #print-order": "printOrder",
			"click #preview-order": "previewOrder",
			"click #new-order": "newOrder",
			"click #cancel-order": "cancelOrder",
			"click #checkout-order": "checkOutOrder",
			"click #refresh-orders": "refreshOrders",
		},
		addLineItem: function () {
			if (!this.model) this.newOrder();

			var $txtBarcode = $('input[name=barcode]');
			var barcode = $txtBarcode.val();
			var tmp = $('input[name=quantity]').val();
			var quantity = 1.0;
			if (tmp && tmp.length > 0) quantity = parseFloat(tmp);

			if (barcode && barcode.length > 1 && quantity > 0) {
				var item = this.model.get('lineItems').find(function (x) {
					return x.get('barcode') == barcode;
				});

				if (item) {
					var q = item.get('quantity');
					item.set({
						'quantity': q + quantity
					});
					this.lstOrders.updateorderitem(this.model.get('orderid'));
				} else {
					var model = this.model;
					var lstOrders = this.lstOrders;
					var _addtoui = this.addItemToUI;
					
					remote.searchItem(barcode, function (data) {
						if (typeof (data) == "string") data = eval('(' + data + ')');
						if (data) {
							if(data.length > 1){
								var compl = _.template($('#tpl-selectitem').html());
								var tr = compl({'items':data});
								$('#tblSelectItem tbody').html(tr);
								$('#tblSelectItem tbody td button').click(function(){
									var id = $(this).data('id')	;
									if(id)
										_addtoui(data[parseInt(id)],model,lstOrders);		
								});
								
								// show pop to select the item
								$('#selectItemModal').modal('show');
							}else{
								addItemToUI(data[0],model,lstOrders);
							}
						}else{
							var ediv = '<div class="alert alert-warning fade in">';
							ediv += 'Oops! There are no items with barcode <b>"'+barcode+'"</b>.';
							ediv += '<a class="close" data-dismiss="alert" href="#">&times;</a>';
							ediv += '</div>';
							$('#statusMessage').html(ediv);
							$(ediv).alert();
						}
					});
				}

				$txtBarcode[0].select(0, barcode.length);
			} else {
				$txtBarcode[0].focus();
			}
		},
		addItemToUI: function(data,model,lstOrders) {
			var itemName = data.Name;
			var price = data.SellPrice;
			var discount = data.Discount;
			var mrp = data.MRP;

			var item = new LineItem({
				orderid: model.get('orderid'),
				slno: model.get('lineItems').length + 1,
				name: itemName,
				barcode: barcode,
				mrp: mrp,
				quantity: quantity,
				price: price,
				discount: discount,
				subtotal: price * quantity
			});

			model.get('lineItems').add(item);
			lstOrders.updateorderitem(model.get('orderid'));
		},
		deleteLineItem: function () {

		},
		newOrder: function () {
			if (this.model) {
				var items = this.model.get('lineItems');
				items.hideUI(function () {
					items.resetRecords();
					items.showUI();
				});
			}

			this.model = new Order;
			this.model.set({
				'lineItems': new LineItemCollection(null, {
					view: this
				})
			});
			this.model.set({
				'payments': new OrderPaymentsCollection(null, {
					view: this
				})
			});

			this.model.bind("change", this.render, this);

			var lstorders = this.lstOrders;
			var currentOrder = this.model;

			remote.newOrder(function (data) {
				if (data) {
					currentOrder.set({
						'id': data.Id,
						'orderid': data.Id,
						'customerid': data.CustomerId,
						'orderno': data.OrderNo,
						'orderdate': data.OrderDate,
						'paidamount': data.PaidAmount,
						'orderamount': data.OrderAmount
					});
					currentOrder.get('lineItems').orderid = data.Id;
					currentOrder.get('payments').orderid = data.Id;
					lstorders.add(currentOrder);
				}
			});
		},
		editOrder: function (orderid) {
			if (!orderid) return;
			if (!this.model) {
				this.model = new Order;
				this.model.bind("change", this.render, this);
			}

			var items = this.model.get('lineItems');
			items.hideUI();
			items.reset();
			items.resetRecords();

			var lstorders = this.lstOrders;
			var currentOrder = this.model;

			$.post('/sales/getorder/' + orderid, null, function (data) {
				if (typeof (data) == "string") data = eval('(' + data + ')');
				if (data) {
					var o = data.order;
					var lineitems = data.lineitems;
					var payments = data.payments;

					currentOrder.set({
						'id': o.Id,
						'orderid': o.Id,
						'customerid': o.CustomerId,
						'orderno': o.OrderNo,
						'orderdate': o.OrderDate,
						'paidamount': o.PaidAmount,
						'orderamount': o.OrderAmount
					});
					currentOrder.get('lineItems').orderid = o.Id;
					currentOrder.get('payments').orderid = o.Id;

					if (lineitems) {
						for (var i = 0; i < lineitems.length; i++) {
							var price = lineitems[i].SellPrice;
							var quantity = lineitems[i].Quantity;
							var no = i + 1;
							var item = new LineItem({
								slno: no,
								name: lineitems[i].Name,
								barcode: lineitems[i].Barcode,
								mrp: lineitems[i].MRP,
								quantity: quantity,
								price: price,
								discount: lineitems[i].Discount,
								subtotal: Math.ceil(price * quantity)
							});
							currentOrder.get('lineItems').add(item);
						}
					}
				}
				items.showUI();
			});
		},
		cancelOrder: function () {
			if (this.model) {
				var items = this.model.get('lineItems');
				items.reset();
				this.lstOrders.updateorderitem(this.model.get('orderid'));
			}
		},
		checkOutOrder: function () {
			this.model.set({
				'orderamount': this.model.get('lineItems').getQAS().totalAmount,
			});
			this.model.save();
		},
		printOrder: function () {

		},
		previewOrder: function () {

		},
		refreshOrders: function () {
			var lstorders = this.lstOrders;
			lstorders.resetUI();
			$.ajax({
				url: '/sales/todayorders',
				accepts: 'application/json',
				contentType: 'application/json',
				data: null,
				dataType: 'json',
				type: 'POST'
			}).done(function (data, textStatus, xhr) {
				if (typeof (data) == "string") data = eval('(' + data + ')');
				if (data && data.length > 0) {
					for (var item = data.length - 1; item >= 0; --item) {
						if (data[item] && data[item].Id) {
							var o = new Order();
							o.set({
								'orderid': data[item].Id,
								'customerid': data[item].CustomerId,
								'orderno': data[item].OrderNo,
								'orderdate': data[item].OrderDate,
								'paidamount': data[item].PaidAmount,
								'orderamount': data[item].OrderAmount
							});
							o.get('lineItems').orderid = data[item].Id;
							o.get('payments').orderid = data[item].Id;
							lstorders.add(o);
						}
					};
				}
			}).fail(function(){
				var ediv = '<div class="alert alert-warning">Oops! Error in loading todays order details.</div>';
				$('#statusMessage').html(ediv);
			});
		}
	});
	
	var salesappview = new SalesAppView;

	$('#tblTodayOrders tbody tr td a').live('click', function (e) {
		var orderid = $(this).parent().parent().data('orderid');
		if (orderid) salesappview.editOrder(orderid);
		return false;
	});
})(jQuery);
