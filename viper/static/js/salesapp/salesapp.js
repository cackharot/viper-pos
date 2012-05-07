/*
 *   Viper POS
 *	salesapp.js
 *	contains backbone based mvc app.
 */
(function ($) {

	LineItem = Backbone.Model.extend({
		defaults: {
			slno: null,
			productid: null,
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
			var subtotal = Math.round(price * quantity);

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

				if (!barcode.startsWith('.')) {
					totalQuantity += quantity;
					totalItems++;
				}

				amt += sbt;
				savings += ((mrp * quantity) - sbt);
			}

			totalQuantity = totalQuantity.toFixed(2);
			amt = Math.round(amt);
			savings = Math.round(savings);
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
			$('#paidAmount').text(0.0);
			$('#balanceAmount').text(0.0);
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
			description: null
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
			lineItems: new LineItemCollection,
			payments: new OrderPaymentsCollection,
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
			$('#tblTodayOrders tbody').prepend(tr)
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
				var odate = item.get('orderdate');
				var amt = item.getOrderAmount();

				var $tr = $('tr[data-orderid="' + orderid + '"]', $('#tblTodayOrders tbody'));
				if ($tr.length > 0) {
					$('.o', $tr).text(orderno);
					$('.c', $tr).text(ToLocalDate(odate));
					$('.a', $tr).text(amt.toFixed(2));
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
			var odate = $.format.date(ToLocalDate(item.get('orderdate')), 'dd-MM-yyyy hh:mm a')
			var pamt = item.get('paidamount');
			var tamt = item.get('orderamount');
			var balance = tamt - pamt;
			$('#orderDate').html(odate);
			$('#orderNumber').html(item.get('orderno'));
			$('#customerName').text(item.get('customername') || '');

			$('#paidAmount').text(pamt);
			$('#balanceAmount').text(Math.abs(balance));
		},
		events: {
			"click #add-item": "addLineItem",
			"click #delete-item": "deleteLineItem",
			"click #print-order": "printOrder",
			"click #preview-order": "previewOrder",
			"click #new-order": "newOrderClick",
			"click #cancel-order": "cancelOrder",
			"click #checkout-order": "checkOutOrder",
			"click #refresh-orders": "refreshOrders",
			"keyup input[name=barcode]": "key_addlineitem",
		},
		key_addlineitem: function (e) {
			if (e.keyCode == 13) this.addLineItem();
		},
		addLineItem: function () {
			if (!this.model) {
				this.newOrder(function () {
					$('#add-item').trigger('click');
				});
				return;
			}
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
							if (data.length > 1) {
								var compl = _.template($('#tpl-selectitem').html());
								var tr = compl({
									'items': data
								});
								$('#tblSelectItem tbody').html(tr);

								$('#tblSelectItem tbody td button').each(function () {
									$(this).click(function () {
										var id = parseInt($(this).data('id'));
										data[id].Quanitity = quantity;
										_addtoui(data[id], model, lstOrders);
										$('#selectItemModal').modal('hide');
										$txtBarcode[0].select(0, barcode.length);
									});
								});

								// show pop to select the item
								$('#selectItemModal').modal('show');
							} else {
								data[0].Quanitity = quantity;
								_addtoui(data[0], model, lstOrders);
							}
						} else {
							showMsg('warn', '<strong>Oops!</strong> There are no items with barcode <span class="label label-info">' + barcode + '</span>.');
						}
					});
				}

				$txtBarcode[0].select(0, barcode.length);
			} else {
				showMsg('warn', '<strong>Enter a valid barcode!</strong>');
				$txtBarcode[0].focus();
			}
		},
		addItemToUI: function (data, model, lstOrders) {
			var barcode = data.Barcode;
			var itemName = data.Name;
			var price = data.SellPrice;
			var discount = data.Discount;
			var mrp = data.MRP;
			var quantity = data.Quanitity;

			var item = new LineItem({
				orderid: model.get('orderid'),
				slno: model.get('lineItems').length + 1,
				productid: data.ProductId,
				name: itemName,
				barcode: barcode,
				mrp: mrp,
				quantity: quantity,
				price: price,
				discount: discount,
				subtotal: Math.round(price * quantity)
			});

			model.get('lineItems').add(item);
			lstOrders.updateorderitem(model.get('orderid'));
		},
		deleteLineItem: function () {

		},
		newOrderClick: function (e) {
			this.newOrder();
		},
		newOrder: function (callback) {
			if (this.model) {
				var items = this.model.get('lineItems');
				items.hideUI(function () {
					items.resetRecords();
					items.showUI();
				});
			}

			this.model = new Order;
			this.model.bind("change", this.render, this);
			this.model.get('lineItems').reset();
			this.model.get('payments').reset();

			var lstorders = this.lstOrders;
			var currentOrder = this.model;

			remote.newOrder(function (data) {
				if (data) {
					currentOrder.set({
						'id': data.Id,
						'orderid': data.Id,
						'customerid': data.CustomerId,
						'customername': data.CustomerName,
						'orderno': data.OrderNo,
						'orderdate': data.OrderDate,
						'paidamount': data.PaidAmount,
						'orderamount': data.OrderAmount
					});
					lstorders.add(currentOrder);
					if (callback) callback()
				}
			});
		},
		editOrder: function (orderid) {
			if (!orderid) return;
			this.model = new Order();
			this.model.bind("change", this.render, this);

			this.model.get('lineItems').reset();
			this.model.get('payments').reset();
			var currentOrder = this.model;
			var items = this.model.get('lineItems');

			items.hideUI(function () {
				items.resetRecords();

				$.post('/sales/getorder/' + orderid, null, function (data) {
					if (typeof (data) == "string") data = eval('(' + data + ')');
					if (data) {
						var o = data.order;
						var orderid = o.Id;
						var lineitems = data.lineitems;
						var payments = data.payments;

						currentOrder.set({
							'id': o.Id,
							'orderid': o.Id,
							'customerid': o.CustomerId,
							'customername': o.CustomerName,
							'orderno': o.OrderNo,
							'orderdate': o.OrderDate,
							'paidamount': o.PaidAmount,
							'orderamount': o.OrderAmount
						});

						if (lineitems) {
							for (var i = 0; i < lineitems.length; i++) {
								var price = lineitems[i].SellPrice;
								var quantity = lineitems[i].Quantity;
								var no = i + 1;
								var item = new LineItem({
									slno: no,
									productid: lineitems[i].ProductId,
									name: lineitems[i].Name,
									barcode: lineitems[i].Barcode,
									mrp: lineitems[i].MRP,
									quantity: quantity,
									price: price,
									discount: lineitems[i].Discount,
									subtotal: Math.round(price * quantity)
								});
								currentOrder.get('lineItems').add(item);
							}
						}

						if (payments) {
							for (var i = 0; i < payments.length; i++) {
								var no = i + 1;
								var item = new OrderPayment({
									slno: no,
									orderid: orderid,
									paidamount: payments[i].PaidAmount,
									paymenttype: payments[i].PaymentType,
									paymentdate: payments[i].PaymentDate,
								});
								currentOrder.get('payments').add(item);
							}
						}

						currentOrder.set({
							'paidamount': currentOrder.getPaidAmount(),
							'orderamount': currentOrder.getOrderAmount(),
						});

						var $txtBarcode = $('input[name=barcode]');
						$txtBarcode[0].select(0, $txtBarcode.val().length);
					}
					items.showUI();
				});
			});
		},
		cancelOrder: function () {
			if (this.model) {
				this.model.get('lineItems').reset();
				this.model.get('payments').reset();
				this.lstOrders.updateorderitem(this.model.get('orderid'));
				this.render();
				var $txtBarcode = $('input[name=barcode]');
				$txtBarcode[0].select(0, $txtBarcode.val().length);
			}
		},
		checkOutOrder: function () {
			if (!this.model || this.model.get('lineItems').length < 1) {
				showMsg('warn', '<strong>Oops!</strong> Order contains no items. Cannot <span class="label label-info">checkout</span>.', false);
				return;
			}

			var orderamt = this.model.getOrderAmount();
			var paidamt = this.model.getPaidAmount();
			var balanceamt = paidamt > orderamt ? 0.0 : (orderamt - paidamt)
			this.model.set({
				'orderamount': orderamt,
				'balanceamount': balanceamt,
			});

			var cmpl = _.template($('#tpl-chkoutorder').html());
			var html = cmpl({
				'item': this.model
			});
			$('#checkoutOrderModel table tbody').html(html);

			$('#checkoutOrderModel').modal('show');

			$('input[name=customername]', $('#checkoutOrderModel')).typeahead({
				idField: 'id',
				idControl: $('input[name=customerid]', $('#checkoutOrderModel')),
				ajax: {
					url: "/customers/search",
					timeout: 500,
					displayField: "name",
					triggerLength: 1,
					method: 'post',
					dataType: 'json',
					loadingClass: "loading-circle",
					preDispatch: function (query) {
						//showLoadingMask(true);
						var fieldName = $('input[type=radio][name=searchfield]:checked').val();
						this.displayField = fieldName;
						return {
							search: query,
							field: fieldName || 'name'
						}
					},
					preProcess: function (data) {
						//showLoadingMask(false);
						if (!data || !data.mylist) return false;
						if (data.success === false) {
							return false;
						}
						if (typeof (data.mylist) == "string") data.mylist = eval('(' + data.mylist + ')');
						// We good!
						return data.mylist;
					}
				}
			});

			$('#btnPayOrder', $('#checkoutOrderModel')).click(this.payOrder);
		},
		payOrder: function () {
			var customerid = $('input[name=customerid]', $('#checkoutOrderModel')).val();

			if (customerid) {
				var orderid = salesappview.model.get('orderid');
				var paidamount = parseFloat($('input[name=paidamount]', $('#checkoutOrderModel')).val());
				var customername = $('input[name=customername]', $('#checkoutOrderModel')).val();
				var paymenttype = $('select[name=paymenttype] option:selected', $('#checkoutOrderModel')).val();
				var orderamount = salesappview.model.getOrderAmount();
				var prevpaidamt = salesappview.model.getPaidAmount();

				if ((paymenttype == 'Cash' && paidamount >= orderamount) || (paymenttype == 'Credit' && paidamount < orderamount) || (paymenttype == 'Card' && paidamount > 0.0) || (paymenttype == 'Cheque' && paidamount > 0.0)) {
					salesappview.model.set({
						'paidamount': paidamount,
						'customerid': customerid,
						'customername': customername,
					});

					var payment = new OrderPayment({
						'orderid': orderid,
						'paidamount': paidamount,
						'paymenttype': paymenttype,
						'paymentdate': new Date().toUTCString(),
					});

					salesappview.model.get('payments').add(payment);
					salesappview.model.save();
					showMsg('success', '<strong>Hooray!</strong> Payment Successfull &amp; Order is saved.');
				} else if (paymenttype == 'Credit' && paidamount >= orderamount) {
					showMsg('warn','<strong>Oops!</strong> Wrong Payment Type. Please choose <span class="label label-info">Cash</span> as payment type if the paid amount is greater than order amount.',false);
				} else {
					showMsg('warn','Paid amount should be greater than or equal to <strong>' + orderamount + '</strong>. Please choose <span class="label label-info">Credit</span> as payment type if the paid amount is lesser than order amount.',false);
				}
			} else {
				showMsg('error', '<strong>Oops!</strong> Please enter a valid customer to save this order.', false);
			}

			$(this).unbind('click', salesappview.payOrder);
			$('#checkoutOrderModel').modal('hide');
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
							lstorders.add(o);
						}
					};
				} else {
					showMsg('info', '<strong>Hmmm!</strong> No orders made today.', false);
				}
			}).fail(function () {
				showMsg('warn', '<strong>Oops!</strong> Error in loading todays order details.', false);
			});
		}
	});

	var salesappview = new SalesAppView;

	$('#tblTodayOrders tbody').on('dblclick', "tr", function (e) {
		$('#tblTodayOrders tbody').find('.active').removeClass('active')
		$(this).addClass('active')
		var orderid = $(this).data('orderid')
		if (orderid) salesappview.editOrder(orderid)
		e.preventDefault()
	});

	function showMsg(type, message, timeout) {
		var ediv = '<div class="alert ';
		if (type == "error") {
			ediv += 'alert-error';
		} else if (type == "info") {
			ediv += 'alert-info';
		} else if (type == "success") {
			ediv += 'alert-success';
		} else if (type == "warn") {
			ediv += 'alert-warning';
		} else {
			ediv += '';
		}
		ediv += ' fade in">';
		ediv += message;
		ediv += '<a class="close" data-dismiss="alert" href="#">&times;</a>';
		ediv += '</div>';
		$('#statusMessage').html(ediv);
		$('.alert', $('#statusMessage')).alert();

		if (timeout || timeout == undefined) {
			setTimeout(function () {
				$('.alert', $('#statusMessage')).alert('close');
			}, 8000);
		}
	}

	String.prototype.startsWith = function (needle) {
		return (this.indexOf(needle) == 0);
	};

	function listen(e) {
		//console.log(e.type)
		//console.log(e.keyCode)
		var isHandled = false;
		switch (e.keyCode) {
		case 114:
			//new order
			isHandled = true
			$('#new-order').trigger('click');
			break;
		case 115:
			//cancel order
			isHandled = true
			$('#cancel-order').trigger('click');
			break;
		case 116:
			//checkout order
			isHandled = true
			$('#checkout-order').trigger('click');
			break;
		case 122:
			//print order
			isHandled = true
			$('#print-order').trigger('click');
			break;
		case 123:
			//preview order
			isHandled = true
			$('#preview-order').trigger('click');
			break;
		}
		if (isHandled) e.preventDefault()
	}

	$(document).bind('keypress', listen);
})(jQuery);
