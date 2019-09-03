
// function orderPrep()
// {
//     // console.log('[BEFORE D3]');

//     d3.json('/order_prep_time', function (data)
//     {
//         // console.log('[INSIDE D3]');

//         console.log(data);
//         var monkey = data;
//         var prepAvg = d3.mean(monkey, function(d) { return d.prepTime; });
//         console.log(prepAvg);

//         textSVG = d3.select('#importData')
//                     .append('div')
//                     .html('<p>Prepare Time Average (Days): '+Math.round(prepAvg, 2)+'</p>')
//     })
//     // console.log('[AFTER D3]', data);
// }

// orderPrep();


function pendingReviews()
{
    // console.log('[BEFORE D3]');

    d3.json('/pending_reviews', function (data)
    {
        var PANEL = d3.select('#reviewsBody');
        PANEL.html('');

        data.forEach(obj => {
            var test = PANEL.append("tr");
            Object.entries(obj).forEach(([key, value]) => {
                if (key == "c_orderURL"){
                    test.append("td").html('<a href=' + value + ' target="_blank">Request Review</a>');
                }
                else if (key == "orderID"){
                    //do nothing
                }
                else if (key == "b_daysSinceShipped"){
                    test.append("td").text(`${value}`+' days');
                }
                else{
                    test.append("td").text(`${value}`);
                }
            });
        });
    });
    // console.log('[AFTER D3]', data);
}

pendingReviews();

function openOrders()
{
    // console.log('[BEFORE D3]');

    d3.json('/open_orders', function (data)
    {
        var PANEL = d3.select('#openOrdersBody');
        PANEL.html('');

        data.forEach(obj => {
            var test = PANEL.append("tr");
            Object.entries(obj).forEach(([key, value]) => {
                if (key == "eorderURL"){
                    test.append("td").html('<a href=' + value + ' target="_blank">View Order</a>');
                }
                else if (key == "dtimeLeft"){
                    test.append("td").text(`${value}`);
                }
                else{
                    test.append("td").text(`${value}`);
                }
            });
        });
    });
    // console.log('[AFTER D3]', data);
}

openOrders();

function orderStats()
{
    // console.log('[BEFORE D3]');

    d3.json('/order_stats', function (data)
    {
        var PANEL = d3.select('#orderStatsBody');
        PANEL.html('');

        data.forEach(obj => {
            var test = PANEL.append("tr");
            Object.entries(obj).forEach(([key, value]) => {
                if (key == "avgOrderTime"){
                    test.append("td").text(`${value}`);
                }

                else{
                    test.append("td").text(`${value}`);
                }
            });
        });
    });
    // console.log('[AFTER D3]', data);
}

orderStats();

// function shopRank()
// {
//     // console.log('[BEFORE D3]');

//     d3.json('/shop_rank', function (data)
//     {
//         var PANEL = d3.select('#shopRank');
//         PANEL.html('');

//         data.forEach(obj => {
//             var test = PANEL.append("tr");
//             Object.entries(obj).forEach(([key, value]) => {

//                     test.append("td").text(`${value}`);
//             });
//         });
//     });
//     // console.log('[AFTER D3]', data);
// }

// shopRank();

// function shopAge()
// {

//     d3.json('/shop_age', function (data)
//     {
//         var PANEL = d3.select('#shopAge');
//         PANEL.html('');

//         data.forEach(obj => {
//             var test = PANEL.append("tr");
//             Object.entries(obj).forEach(([key, value]) => {

//                     test.append("td").text(`${value}`+' days');
//             });
//         });
//     });
// }

// shopAge();

function listStats()
{

    d3.json('/list_stats', function (data)
    {
        var PANEL = d3.select('#listStats');
        PANEL.html('');

        data.forEach(obj => {
            var test = PANEL.append("tr");
            Object.entries(obj).forEach(([key, value]) => {

                    test.append("td").text(`${value}`);
            });
        });
    });
}

listStats();

function bayes()
{
    // console.log('[BEFORE D3]');

    d3.json('/bayes', function (data)
    {
        var PANEL = d3.select('#bayesTestTable');
        PANEL.html('');

        data.forEach(obj => {
            var test = PANEL.append("tr");
            Object.entries(obj).forEach(([key, value]) => {
                if (key == "i_EditURL"){
                    test.append("td").html('<a href=' + value + ' target="_blank">Edit Listing</a>');
                }
                else{
                    test.append("td").text(`${value}`);
                }
            });
        });
    });
    // console.log('[AFTER D3]', data);
}

bayes();