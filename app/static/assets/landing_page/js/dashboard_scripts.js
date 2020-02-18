$(document).ready(function () {
    $.get('/my_course_views', function (result) {
        var my_views = JSON.parse(result);
        google.charts.load('current', {'packages': ['corechart']});
        google.charts.setOnLoadCallback(drawChart);

        function drawChart() {
            var data = new google.visualization.DataTable();
            data.addColumn('string', 'Topping');
            data.addColumn('number', 'Slices');
            data.addRows(my_views);
            var options = {
                'title': 'Pie Chart',
                'width': '100%',
                'height': '100%'
            };
            var chart = new google.visualization.PieChart(document.getElementById('pie_div'));
            chart.draw(data, options);

            var temp_data = [["Element", "Density", {role: "style"}]];
            my_views.forEach(function (item, index) {
                temp_data.push(item.concat('silver'));
            });

            var data2 = google.visualization.arrayToDataTable(temp_data);

            var view2 = new google.visualization.DataView(data2);
            view2.setColumns([0, 1,
                {
                    calc: "stringify",
                    sourceColumn: 1,
                    type: "string",
                    role: "annotation"
                },
                2]);

            var options2 = {
                title: "Bar Chart",
                width: 600,
                height: 400,
                bar: {groupWidth: "95%"},
                legend: {position: "none"},
            };
            var chart2 = new google.visualization.ColumnChart(document.getElementById("columnchart_values"));
            chart2.draw(view2, options2);
        }
    });
});