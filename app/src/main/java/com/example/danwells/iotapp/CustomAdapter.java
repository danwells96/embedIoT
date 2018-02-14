package com.example.danwells.iotapp;

import android.app.Activity;
import android.support.annotation.LayoutRes;
import android.support.annotation.NonNull;
import android.support.annotation.Nullable;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

/**
 * Created by danwells on 12/02/2018.
 */

public class CustomAdapter extends ArrayAdapter{

    private final Activity contxt;
    private final String[] nameValues;
    private final String[] actionValues;
    private final String[] timeValues;

    public CustomAdapter(@NonNull Activity context, @LayoutRes int resource, @NonNull String[] names, String[] actions, String[] times) {
        super(context, R.layout.notification_card, names);
        this.contxt = context;
        this.nameValues = names;
        this.actionValues = actions;
        this.timeValues = times;
    }

    @NonNull
    @Override
    public View getView(int position, @Nullable View convertView, @NonNull ViewGroup parent) {
        LayoutInflater inflater = contxt.getLayoutInflater();
        View rowView = inflater.inflate(R.layout.notification_card, parent, false);
        TextView nameView = (TextView) rowView.findViewById(R.id.notificationName);
        TextView actionView = (TextView) rowView.findViewById(R.id.notificationAction);
        TextView timeView = (TextView) rowView.findViewById(R.id.notificationTime);
        nameView.setText(nameValues[position]);
        actionView.setText(actionValues[position]);
        timeView.setText(timeValues[position]);
        return rowView;
    }

}
